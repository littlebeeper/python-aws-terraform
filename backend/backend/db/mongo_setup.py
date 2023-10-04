import functools

from backend.config import DbConfig, Config
from backend.config_deps import app_config

import pymongo

from backend.env import Environment


def get_db():
    client = get_mongo_client()
    return client[app_config().mongo_db_config.db_name]

@functools.cache
def get_mongo_client(db_config: DbConfig = None):
    if db_config is None:
        config: Config = app_config()
        db_config = config.mongo_db_config
        if config.env == Environment.DEVELOPMENT:
            print('db_config:', db_config)

    uri = f'{db_config.driver}://{db_config.username}:{db_config.password}@{db_config.host}/{db_config.db_name}{db_config.uri_params}'

    client = pymongo.mongo_client.MongoClient(
        uri,
        port=27017,
        tz_aware=False,
        connect=True,
    )

    return client


