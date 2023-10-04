from __future__ import annotations
from typing import Dict, Generic, Type, TypeVar, Any

from pydantic.main import BaseModel

from backend.db.model.model import Model

TModel = TypeVar('TModel', bound=BaseModel)


class Builder(Generic[TModel]):
    model: Type[TModel]
    values: Dict[str, object]

    def __init__(self, model_class: Type[TModel], existing_model: TModel = None) -> None:
        super().__setattr__('model', model_class)
        if existing_model:
            super().__setattr__('values', dict(existing_model))
        else:
            values_map = {}
            if issubclass(model_class, Model):
                values_map = model_class.base_kwargs()
            super().__setattr__('values', values_map)

    def __setattr__(self, name: str, value: object) -> None:
            self.values[name] = value

    def __iadd__(self, name: str, new_entries: list[object]):
        values = self.__getattr__(name)
        values += new_entries
        self.__setattr__(name, values)

    def __getattr__(self, name: str) -> Any:
        return self.values[name]

    def build(self) -> TModel:
        return self.model(**self.values)
