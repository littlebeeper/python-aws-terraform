import argparse

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.mongo_setup import get_mongo_client, get_db

from backend.env import Environment
from backend.scripts.helpers import setup_env

from bpython import embed



def main():
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        embed(locals_=dict(globals(), **locals()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a new account with a unique name')

    parser.add_argument('--env', '-e',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Environment._member_names_],
                        help='Environment')

    args = parser.parse_args()
    specified_env = Environment[args.env.upper()]
    if specified_env == Environment.TEST:
        setup_env(specified_env, cwd_depth_from_backend_root=0, allow_test_env=True)
    else:
        setup_env(specified_env, cwd_depth_from_backend_root=0)

    main()

