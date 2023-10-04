from typing import Optional

from backend.db.mongo_db import MongoDb
from backend.db.model.user_account_access import UserAccountAccess


class UserAccountAccessDb(MongoDb):
    model = UserAccountAccess

    def get_account_id(self, email) -> Optional[str]:
        access = self.get_for_email(email)
        if access is None:
            return None
        return access.account_id

    def get_for_email(self, email) -> Optional[UserAccountAccess]:
        accesses = list(self.query({'email': email}))
        if len(accesses) == 0:
            return None
        elif len(accesses) == 1:
            return accesses[0]
        else:
            raise Exception(f'Multiple accounts for the same email: {email}')
