from typing import ClassVar

from backend.api.auth.permission import Permission
from backend.db.model.account_specific_model import AccountSpecificModel


class UserAccountAccess(AccountSpecificModel):
    token_prefix: ClassVar[str] = 'uaa'
    __collection__ = 'user_account_access'

    email: str
    permissions: list[Permission] = []
    signed_tos: bool = False
