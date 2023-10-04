from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from backend.db.model import Account
from backend.oauth import is_oauth_active, GITHUB_PROVIDER_CONFIG_KEY, JIRA_PROVIDER_CONFIG_KEY, \
    ASANA_PROVIDER_CONFIG_KEY, BOX_PROVIDER_CONFIG_KEY
from backend.api.auth.integration import auth
from backend.api.routers.custom_router import SrvRoute

from backend.api.request_context_deps import get_mongo_db_session, \
    get_user_id_account_id_and_email
from backend.db.mongo_db_session import DbSession

from propelauth_fastapi import User

router = APIRouter(route_class=SrvRoute)


class SessionContext(BaseModel):
    account_id: str
    email: str
    signed_tos: bool
    user_id: str
    gates: list[str] = []


@router.get('', tags=['session'], response_model=SessionContext)
def get_session(
        user: User = Depends(auth.require_user),
        dbs: DbSession = Depends(get_mongo_db_session)
):
    user_id, account_id, email = get_user_id_account_id_and_email(user, dbs)

    account: Account = dbs.accounts_db.load_one(account_id)
    user_account_access = dbs.user_account_access_db.get_for_email(email=email)

    gates = set()
    for key, value in account.gates.items():
        if value:
            gates.add(key)

    return SessionContext(
        user_id=user_id,
        account_id=account_id,
        email=email,
        gates=list(gates),
        signed_tos=user_account_access.signed_tos,
    )


class OAuthStatus(BaseModel):
    github: bool
    jira: bool
    asana: bool
    # TODO: remove this
    account_id: str


@router.get('/oauth_status', tags=['session'], response_model=OAuthStatus)
async def get_active_oauth_sessions(
        user: User = Depends(auth.require_user),
        dbs: DbSession = Depends(get_mongo_db_session)
):
    _, account_id, _ = get_user_id_account_id_and_email(user, dbs)

    return {
        'jira': is_oauth_active(account_id, JIRA_PROVIDER_CONFIG_KEY),
        'github': is_oauth_active(account_id, GITHUB_PROVIDER_CONFIG_KEY),
        'asana': is_oauth_active(account_id, ASANA_PROVIDER_CONFIG_KEY),
        'box': is_oauth_active(account_id, BOX_PROVIDER_CONFIG_KEY),
        'account_id': account_id,
    }


@router.post('/sign_tos', tags=['tos'], response_model=SessionContext)
def sign_tos(
        user: User = Depends(auth.require_user),
        dbs: DbSession = Depends(get_mongo_db_session)
):
    user_id, account_id, email = get_user_id_account_id_and_email(user, dbs)

    user_account_access = dbs.user_account_access_db.get_for_email(email=email)
    user_account_access.signed_tos = True
    dbs.user_account_access_db.update_obj(user_account_access)

    return get_session(
        user=user,
        dbs=dbs,
    )
