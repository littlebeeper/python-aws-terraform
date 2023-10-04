from typing import Optional
from pydantic import BaseModel


class UpdateAccountSettingsRequest(BaseModel):
    name: Optional[str]
