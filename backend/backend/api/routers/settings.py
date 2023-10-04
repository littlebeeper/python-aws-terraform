from fastapi import APIRouter, Depends
from propelauth_py.user import User as PropelUser
from pydantic import BaseModel

from backend.api.auth.integration import auth
from backend.api.request_context_deps import get_user_id_account_id_and_email, get_mongo_db_session
from backend.api.routers.custom_router import SrvRoute
from backend.api.routers.request_response import UpdateAccountSettingsRequest
from backend.db.model import Account
from backend.db.model.builder import Builder
from backend.db.mongo_db_session import DbSession

router = APIRouter(route_class=SrvRoute)


class AccountSettings(BaseModel):
    name: str = 'example'


@router.get('', tags=['settings'], response_model=AccountSettings)
def get_account_settings(
        user: PropelUser = Depends(auth.require_user),
        dbs: DbSession = Depends(get_mongo_db_session)
):
    _, account_id, _ = get_user_id_account_id_and_email(user, dbs)

    account = dbs.accounts_db.load_one(obj_id=account_id)

    return AccountSettings(
        name=account.name,
    )


@router.post('', tags=['settings'], response_model=AccountSettings)
def update_account_settings(
        request: UpdateAccountSettingsRequest,
        user: PropelUser = Depends(auth.require_user),
        dbs: DbSession = Depends(get_mongo_db_session)
):
    user_id, account_id, _ = get_user_id_account_id_and_email(user, dbs)

    account = dbs.accounts_db.load_one(obj_id=account_id)
    account_builder = Builder(model_class=Account, existing_model=account)

    if request.name is not None:
        account_builder.name = request.name

    dbs.accounts_db.update_obj(account_builder.build())

    return AccountSettings(
        name=account_builder.name,
    )
