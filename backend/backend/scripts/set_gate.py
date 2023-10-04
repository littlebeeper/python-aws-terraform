import argparse

from backend.db.model.builder import Builder
from backend.db.mongo_db_session import DbSessionMaker, DbSession
from backend.db.model import Account
from backend.db.mongo_setup import get_db, get_mongo_client

from backend.env import Environment
from backend.scripts.helpers import setup_env

def set_gate(dbs: DbSession, account_id: str, gate_name: str, enabled: bool):
    account = dbs.accounts_db.load_one(account_id)
    account_builder = Builder(Account, existing_model=account)
    existing_gates = account.gates

    existing_gates[gate_name] = enabled
    account_builder.gates = existing_gates
    dbs.accounts_db.update_obj(account_builder.build())

    print(f'Done. Account {account_id} now has gates {existing_gates}')

def main(account_id, gate_name, enabled):
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        set_gate(dbs, account_id, gate_name, enabled)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool set gates on accounts")

    parser.add_argument('--env', '-e',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Environment._member_names_],
                        help='Environment')

    parser.add_argument('--account_id', '-a',
                        type=str,
                        required=True,
                        help='Account ID')

    parser.add_argument('--gate_name', '-g',
                        type=str,
                        required=True,
                        help='Gate name')

    parser.add_argument('--enable', '-s',
                        action='store_true',
                        default=None,
                        help='Enable the gate on the account')

    parser.add_argument('--disable', '-d',
                        dest='enable',
                        action='store_false',
                        default=None,
                        help='Disable the gate on the account')

    args = parser.parse_args()
    specified_env = Environment[args.env.upper()]
    setup_env(specified_env, cwd_depth_from_backend_root=0)

    # validate args
    if args.enable is None:
        raise Exception('Must specify --enable or --disable')

    print(args.enable)

    main(args.account_id, args.gate_name, args.enable)