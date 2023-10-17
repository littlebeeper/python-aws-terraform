import argparse

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.model import Account, UserAccountAccess
from backend.db.mongo_setup import get_db, get_mongo_client
from backend.env import Environment
from backend.scripts.helpers import setup_env

DEFAULT_ACCOUNT_ID = 'acct_66bb3be7044343ca84803551c82ec9a0'


def main(email):
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        # check if account already exists
        account = dbs.accounts_db.load_one(DEFAULT_ACCOUNT_ID)
        if account is not None:
            print(f'Account "{account.name}" already exists')
        else:
            print(f'Creating default account')
            account = Account(id=DEFAULT_ACCOUNT_ID, name='Default Account')
            dbs.accounts_db.add_obj(account)

        # check if user_account_access already exists
        user_account_access = dbs.user_account_access_db.query_one({"email": email, "account_id": DEFAULT_ACCOUNT_ID})
        if user_account_access is not None:
            print(f'UserAccountAccess for "{email}" already exists')
        else:
            print(f'Creating UserAccountAccess for "{email}"')
            user_account_access = UserAccountAccess(
                email=email,
                account_id=DEFAULT_ACCOUNT_ID,
                permissions=['read', 'write'])
            dbs.user_account_access_db.add_obj(user_account_access)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initialize account, user_account_access")

    parser.add_argument("--email", "-em", type=str, help="Email of the user to create")
    parser.add_argument("--env", "-e", type=str, choices=[x.lower() for x in Environment._member_names_], help="Environment to use")

    args = parser.parse_args()

    specified_env = Environment[args.env.upper()]
    setup_env(specified_env, cwd_depth_from_backend_root=0)
    main(args.email)
