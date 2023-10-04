from pydantic import BaseModel

class AbstractParam(BaseModel):
    pass

    class Config:
        use_enum_values = True
