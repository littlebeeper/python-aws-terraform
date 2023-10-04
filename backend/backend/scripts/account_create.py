import argparse

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.model.account import Account
from backend.db.mongo_setup import get_mongo_client, get_db

from backend.env import Environment
from backend.scripts.helpers import setup_env

from backend.scripts.give_email_access_to_account import main as give_email_access_to_account
from backend.api.auth.permission import Permission
from backend.scripts.set_gate import set_gate


def main(name, id=None, emails=None, gates=None):
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        if dbs.accounts_db.count(dict(name=name)) > 0:
            raise Exception(f'Account with name "{name}" already exists')

        new_account = Account(id=id, name=name)
        dbs.accounts_db.add_obj(new_account)
        account_id = new_account.id
        print("Created new account with id: {0}".format(account_id))

        if emails is not None and len(emails) > 0:
            give_email_access_to_account(
                account_id=account_id,
                raw_emails=emails,
                permissions={
                    Permission.READ,
                    Permission.WRITE,
                })

        if gates is not None and len(gates) > 0:
            for gate in gates:
                set_gate(dbs=dbs, account_id=account_id, gate_name=gate, enabled=True)

        return account_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a new account with a unique name')

    parser.add_argument('--env', '-e',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Environment._member_names_],
                        help='Environment')

    parser.add_argument('--id', '-i',
                        type=str,
                        required=False,
                        default=None,
                        help='Id of company we are serving. (Optional)')

    parser.add_argument('--name', '-n',
                        type=str,
                        required=True,
                        help='Name of company we are serving. ')

    parser.add_argument('--emails', '-em',
                        nargs='+',
                        required=False,
                        default=[],
                        help='Emails of users to add to the account. ')

    parser.add_argument('--gates', '-g',
                        nargs='+',
                        required=False,
                        default=[],
                        help='Gates to add to the account. ')

    args = parser.parse_args()
    specified_env = Environment[args.env.upper()]
    setup_env(specified_env, cwd_depth_from_backend_root=0)
    main(id=args.id, name=args.name, emails=args.emails, gates=args.gates)
