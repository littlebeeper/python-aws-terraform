from abc import ABC, abstractmethod
from typing import List, Iterable, Any, Callable, Optional, TypeVar

import logging

from backend.db.model.model import Model

logger = logging.getLogger(__name__)


from pymongo.client_session import ClientSession
from pymongo.database import Database
from pymongo.collection import Collection

class UnexpectedDbState(Exception):
    def __init__(self, msg):
        super(UnexpectedDbState, self).__init__(msg)

MODEL = TypeVar("M", bound=Model)

logger = logging.getLogger(__name__)


class MongoDb(ABC):
    def __init__(self, db: Database, session: ClientSession):
        self.collection: Collection = db.__getattr__(self.model.__collection__)
        self.session: ClientSession = session
        assert set(self.model.get_fields()).issuperset(set(self.deserializers.keys()))
        assert set(self.model.get_fields()).issuperset(set(self.serializers.keys()))

    def _validate_obj(self, obj: MODEL) -> None:
        if type(obj) != self.model:
            raise TypeError(f'Expected {self.model.__name__} but got {type(obj).__name__} obj')

    @property
    @abstractmethod
    def model(self) -> MODEL:
        pass

    @property
    def serializers(self):
        return {}

    @property
    def deserializers(self):
        return {}

    def add_obj(self, obj: MODEL) -> None:
        self._validate_obj(obj)
        logger.info(f'DB:ADD_OBJ: {obj.id}: \n{obj.serialize()}')
        self.collection.insert_one(document=obj.serialize(), session=self.session)

    def update_obj(self, obj: MODEL) -> None:
        self._update_obj(obj)

    def _update_obj(self, obj: MODEL) -> None:
        self._validate_obj(obj)
        logger.info(f'DB:UPDATE_OBJ:{obj.id}: \n{obj.serialize()}')
        self.collection.find_one_and_replace(filter={'_id': obj.id}, replacement=obj.serialize(), session=self.session)

    def delete_many(self, obj_ids, account_id=None) -> None:
        if account_id:
            logger.info(f'DB:DELETE_MANY:{", ".join(obj_ids)} for account {account_id}')
            self.collection.delete_many(
                filter={'_id': {'$in': obj_ids}, 'account_id': account_id}, session=self.session)
        else:
            logger.info(f'DB:DELETE_MANY:{", ".join(obj_ids)}')
            self.collection.delete_many(
                filter={'_id': {'$in': obj_ids}}, session=self.session)

    def load_all(self, account_id=None) -> list[MODEL]:
        return list(self.query({}, account_id=account_id))

    def count(self, filter_dict=None, account_id=None) -> int:
        filter_dict = self.resolve_filters(filter_dict, account_id=account_id)
        return self.collection.count_documents(filter=filter_dict, session=self.session)

    def query_one(self, filter_dict=None, account_id=None) -> Optional[MODEL]:
        results = list(self.query(filter_dict, account_id))
        if len(results) > 1:
            raise UnexpectedDbState(f'Expected 1 result, got {len(results)}')

        if len(results) == 0:
            return None

        return results[0]

    def query(self, filter_dict=None, account_id=None) -> Iterable[MODEL]:
        filter_dict = self.resolve_filters(filter_dict, account_id)

        return DeserializingIterable(
            iterable=self.collection.find(filter=filter_dict, session=self.session),
            deserializer=lambda dct: self.model.from_dict(dct),
        )

    def exists(self, filter_dict=None, account_id=None) -> bool:
        filter_dict = self.resolve_filters(filter_dict, account_id)
        return self.collection.count_documents(filter=filter_dict, session=self.session) > 0

    def load_many(self, obj_ids, account_id=None) -> list[MODEL]:
        return list(self.query(filter_dict={'_id': {'$in': list(obj_ids)}}, account_id=account_id))

    def load_one(self, obj_id: str, account_id=None) -> Optional[MODEL]:
        maybe_obj = self.collection.find_one(self.resolve_filters({'_id': obj_id}, account_id=account_id), session=self.session)
        if maybe_obj is None:
            return None
        return self.model.from_dict(maybe_obj)

    def resolve_filters(self, filter_dict=None, account_id=None) -> dict:
        if filter_dict is None:
            filter_dict = {}

        if account_id:
            filter_dict['account_id'] = account_id

        for field, value in self.model.__fields__.items():
            if field in filter_dict and value is not None and value.alias is not None:
                swap = filter_dict[field]
                del filter_dict[field]
                filter_dict[value.alias] = swap

        return filter_dict

    def raw_find(self, filter_dict=None, sort=None, limit=10):
        return DeserializingIterable(
            iterable=self.collection.find(filter=filter_dict, sort=sort, limit=limit, session=self.session),
            deserializer=lambda dct: self.model.from_dict(dct))

class DeserializingIterable(Iterable[MODEL]):

    def __init__(self, iterable, deserializer: Callable[[Any], MODEL]):
        self.iterable = iterable
        self.deserializer = deserializer

    def __iter__(self):
        return self

    def __next__(self):
        next_obj = next(self.iterable)
        return self.deserializer(next_obj)
