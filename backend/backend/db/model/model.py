import enum
import uuid
from abc import abstractmethod

from datetime import datetime
from pydantic import Field, BaseModel

class Model(BaseModel):
    id: str = Field(alias='_id')
    created: datetime = Field(default_factory=lambda: datetime.utcnow().replace(microsecond=0))

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if 'id' in kwargs:
            # if 'id' in kwargs and kwargs['id'] but is none, then ignore it.
            if kwargs['id'] is not None:
                kwargs['_id'] = kwargs['id']
            del kwargs['id']

        if '_id' in kwargs and not self._is_suggested_id_valid(kwargs['_id']):
            raise ValueError(f"Invalid _id {kwargs['_id']} for model {self.__class__}")

        # if 'id' not in kwargs and '_id' not in kwargs:
        #     if "EmployeeModel" == self.__class__.__name__:
        #         raise ValueError("Testing")

        kwargs = self.__class__.base_kwargs(**kwargs) | kwargs
        super(Model, self).__init__(**kwargs)

    @classmethod
    def base_kwargs(cls, **kwargs):
        return {
            "_id": cls._generate_model_id(**kwargs),
        }

    class Config:
        use_enum_values = True

    def serialize(self):
        return {k: serialize_helper(v, {}) for k, v in self.dict(by_alias=True).items()}

    @classmethod
    def deserialize(cls, serializable_object_dict):
        return cls.parse_obj(serializable_object_dict)

    @classmethod
    def deserialize_from_json(cls, json_string):
        return cls.parse_raw(json_string)

    @classmethod
    def get_fields(cls):
        return [fld for fld in cls.__fields__.keys()]

    def get_field_descriptors(self):
        return self.__fields__

    @property
    @abstractmethod
    def token_prefix(self):
        pass

    @property
    @abstractmethod
    def __collection__(self):
        pass

    def to_dict(self):
        return self.dict(by_alias=True)

    def created_date(self):
        return self.created.date()

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    @classmethod
    def get_field_type(cls, field_name):
        return cls.__dict__[field_name].type

    @classmethod
    def _generate_model_id(cls, **kwargs):
        return f"{cls.token_prefix}_{uuid.uuid4().hex}"

    def _is_suggested_id_valid(self, id):
        if id is None:
            return False

        if not id.startswith(self.token_prefix):
            return False

        return True

def serialize_helper(sub_model, encoding_map={}):
    if isinstance(sub_model, list):
        return [serialize_helper(sub, encoding_map) for sub in sub_model]
    elif isinstance(sub_model, dict):
        return {k: serialize_helper(v, encoding_map) for k, v in sub_model.items()}
    elif isinstance(sub_model, Model):
        raise ValueError(f"Nesting of models is not supported. Nested model: {sub_model}")
    elif isinstance(sub_model, enum.Enum):
        return sub_model.value
    else:
        return sub_model
