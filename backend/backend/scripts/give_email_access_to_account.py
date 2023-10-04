import argparse

from backend.api.auth.permission import Permission
from backend.db.model.builder import Builder
from backend.db.mongo_db_session import DbSessionMaker
from backend.db.model import UserAccountAccess
from backend.db.mongo_setup import get_mongo_client, get_db
from backend.env import Environment
from backend.scripts.helpers import setup_env, validate_and_normalize_email


def main(account_id, raw_emails, permissions: set[Permission]):
    emails = set()
    for email in set(raw_emails):
        emails.add(validate_and_normalize_email(email))

    permissions_values = [permission.name.lower() for permission in permissions]

    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        for email in emails:
            existing_user_account_access = dbs.user_account_access_db.query_one(dict(email=email), account_id=account_id)
            if existing_user_account_access and set(existing_user_account_access.permissions) == set(permissions):
                print(f'Email {email} already has access to account {account_id} with permissions {permissions_values}')
                continue

            user_account_access_builder = Builder(model_class=UserAccountAccess, existing_model=existing_user_account_access)
            user_account_access_builder.email = email
            user_account_access_builder.account_id = account_id
            user_account_access_builder.permissions = list(permissions)
            print(f'Adding email {email} to account {account_id} with permissions {permissions_values}')
            if existing_user_account_access:
                dbs.user_account_access_db.update_obj(user_account_access_builder.build())
            else:
                dbs.user_account_access_db.add_obj(user_account_access_builder.build())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to convert the output of our new or old pipeline'
                                                 'into a format consumable by our airtable UI')

    parser.add_argument('--env', '-e',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Environment._member_names_],
                        help='Environment')

    parser.add_argument('--account', '-acct',
                        type=str,
                        required=True,
                        default=None,
                        help='Generated account id')

    parser.add_argument('--emails', '-em',
                        type=str,
                        required=True,
                        nargs='+',
                        help="Emails that will be granted access to account")

    parser.add_argument('--permissions', '-p',
                        type=str,
                        required=True,
                        nargs='+',
                        help="Permissions that will be granted to the emails")

    args = parser.parse_args()
    specified_env = Environment[args.env.upper()]
    setup_env(specified_env, cwd_depth_from_backend_root=0)

    specified_permissions = [Permission[x.upper()] for x in args.permissions]

    main(
        raw_emails=args.emails,
        account_id=args.account,
        permissions=set(specified_permissions))
