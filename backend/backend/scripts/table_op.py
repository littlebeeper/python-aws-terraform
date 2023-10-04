import argparse

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.model import Account, UserAccountAccess
from backend.db.mongo_setup import get_db, get_mongo_client

from backend.env import Environment
from backend.scripts.helpers import setup_env

from enum import Enum

MAX_RESULTS = 100
class Action(Enum):
    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4

type_coercion_map = {
}


def query_string_to_dict(query_string=None):
    if query_string is None:
        return {}
    return dict(x.split("=") for x in query_string.split("&"))

def resolve_db(dbs, table_name):
    if table_name == 'accounts':
        return dbs.accounts_db
    elif table_name == 'calls':
        return dbs.calls_db
    elif table_name == 'clusters':
        return dbs.clusters_db
    elif table_name == 'cluster_snippet_joins':
        return dbs.cluster_snippet_joins_db
    elif table_name == 'snippets':
        return dbs.snippets_db
    elif table_name == 'user_account_access':
        return dbs.user_account_access_db
    elif table_name == 'accounting_config':
        return dbs.accounting_config_db
    else:
        raise Exception(f'No database resolved for table "{table_name}"')


def coerce_field_value(model, field_name, field_value_string):
    return type_coercion_map[model.get_field_type(field_name).__class__](field_value_string)


def are_you_sure(action, old_objs, new_objs):
    print("You are about to perform the following action:")
    print(f"Action: {action}")
    print(f"Previous: ")
    pretty(old_objs, ', ')
    print(f"Updated : ")
    pretty(new_objs, ', ')
    sure = input('Are you sure you want to proceed? [y/N] ').lower() == 'y'
    if sure:
        print('Proceeding...')
        return True
    else:
        print('Aborting...')
        return False


def pretty(objs, sep='\n'):
    print(sep.join([str(dict(obj)) for obj in objs]))

COLLECTIONS = [
    Account.__collection__,
    UserAccountAccess.__collection__,
]

def main(table_name, action, query_string=None, field_string=None, test=False):
    if table_name not in COLLECTIONS:
        raise Exception(f'Table with name "{table_name}" does not exist')

    query = query_string_to_dict(query_string)

    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
            db = resolve_db(dbs, table_name)

            if action == Action.CREATE:
                fields_for_create = query_string_to_dict(field_string)
                # we get the coercion somewhat for free
                # https://github.com/pydantic/pydantic/issues/578
                new_obj = db.model(**fields_for_create)
                if are_you_sure(action, [], [new_obj]):
                    db.add_obj(new_obj)

            elif action == Action.READ:
                if db.count(query) > MAX_RESULTS:
                    raise Exception(f'Query returned more than {MAX_RESULTS} results. Please narrow your query.')
                pretty(list(db.query(query)))

            elif action == Action.UPDATE:
                assert len(query) == 1 and 'id' in query, 'Update queries must specify exactly one id'
                existing_object = db.load_one(obj_id=query['id'])
                if not existing_object:
                    raise Exception(f'No object with id "{query["id"]}" exists')

                fields_to_update = query_string_to_dict(field_string)
                object_dict_to_update = dict(existing_object)
                for field_name, field_value_string in fields_to_update.items():
                    object_dict_to_update[field_name] = field_value_string
                # we get the coercion somewhat for free
                # https://github.com/pydantic/pydantic/issues/578
                updated_obj = db.model(**object_dict_to_update)
                if are_you_sure(action, [existing_object], [updated_obj]):
                    db.update_obj(updated_obj)

            elif action == Action.DELETE:
                objs_to_delete = list(db.query(query))
                assert len(objs_to_delete) == 1 # just to prevent accidental mass deletes
                if are_you_sure(action, objs_to_delete, []):
                    db.delete_many([x.id for x in objs_to_delete])

            else:
                raise Exception(f'Action "{action}" not supported')

    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to read and make changes to tables")

    parser.add_argument('--env', '-e',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Environment._member_names_],
                        help='Environment')

    parser.add_argument('--table_name', '-n',
                        type=str,
                        required=True,
                        choices=COLLECTIONS,
                        help='Name of company we are serving. ')

    parser.add_argument('--action', '-a',
                        type=str,
                        required=True,
                        choices=[x.lower() for x in Action._member_names_],
                        help='Action to perform on table')

    parser.add_argument('--query', '-q',
                        type=str,
                        default=None,
                        required=False,
                        help='Query to perform on table')

    parser.add_argument('--fields', '-f',
                        type=str,
                        default=None,
                        required=False,
                        help='Fields relevant to write operation')

    args = parser.parse_args()
    specified_env = Environment[args.env.upper()]
    setup_env(specified_env, cwd_depth_from_backend_root=0)

    specified_action = Action[args.action.upper()]
    main(
        table_name=args.table_name,
        action=specified_action,
        query_string=args.query,
        field_string=args.fields,
    )
