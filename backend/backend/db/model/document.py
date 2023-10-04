from typing import List

from pydantic import BaseModel


class Document(BaseModel):

    def serialize(self):
        return self.dict()

    @classmethod
    def deserialize(cls, serializable_object_dict):
        return cls.parse_obj(serializable_object_dict)

    @classmethod
    def get_fields(cls) -> List[str]:
        return [fld for fld in cls.__fields__.keys()]

    @classmethod
    def get_required_fields(cls) -> List[str]:
        return [fld_key for fld_key, fld_value in cls.__fields__.items() if fld_value.required]
