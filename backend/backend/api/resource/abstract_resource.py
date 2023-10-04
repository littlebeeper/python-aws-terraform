from pydantic import BaseModel

class AbstractResource(BaseModel):
    pass

    class Config:
        use_enum_values = True
