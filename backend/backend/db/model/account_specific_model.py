from abc import ABC

from backend.db.model.model import Model
from odmantic import Field

class AccountSpecificModel(Model, ABC):
    account_id: str = Field(required=True)
