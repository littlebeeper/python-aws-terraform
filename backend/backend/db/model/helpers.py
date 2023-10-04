from typing import TypeVar, Optional, Generic
from pydantic.fields import ModelField

PydanticField = TypeVar("PydanticField")


class EmptyStrToNone(Generic[PydanticField]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: PydanticField, field: ModelField) -> Optional[PydanticField]:
        if v == "":
            return None
        return v
