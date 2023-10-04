from typing import Optional

from backend.db.model import Account
from backend.db.mongo_db_session import DbSession


def account_create(dbs: DbSession, name: str, id: Optional[str]) -> Account:
    new_account: Account = Account(
        id=id,
        name=name,
    )

    dbs.accounts_db.add_obj(new_account)

    return new_account
