from typing import Optional

from fastapi import HTTPException

from backend.api.auth.integration import auth
from backend.api.auth.permission import Permission
from backend.db.mongo_db_session import DbSessionMaker as MongoDbSessionMaker, DbSession as MongoDbSession

from backend.db.mongo_setup import get_db, get_mongo_client

from propelauth_fastapi import User

def get_user_id_account_id_and_email(user: User, dbs: MongoDbSession) -> [str, Optional[str], str]:
    account_id = dbs.user_account_access_db.get_account_id(email=user.email)
    return user.user_id, account_id, user.email

async def get_account_id_and_confirm_permissions(
        user: User,
        dbs: MongoDbSession,
        permissions_necessary: list[Permission]
) -> str:
    email = auth.fetch_user_metadata_by_user_id(user.user_id, include_orgs=False)['email']
    account_accesses = list(dbs.user_account_access_db.query({'email': email}))
    if len(account_accesses) == 0:
        raise HTTPException(status_code=404, detail=f'Email {email} does not have access to any account')
    elif len(account_accesses) == 1:
        account_access = account_accesses[0]
        permissions_found = {Permission(x) for x in account_access.permissions}
        if not permissions_found.issuperset(permissions_necessary):
            raise HTTPException(status_code=403, detail=f'Email {email} does not have the necessary permissions')
        return account_access.account_id
    else:
        raise HTTPException(status_code=500, detail=f'Multiple accounts for the same email: {email}')

def get_mongo_db_session() -> MongoDbSession:
    with MongoDbSessionMaker(get_db(), get_mongo_client()) as db:
        yield db
