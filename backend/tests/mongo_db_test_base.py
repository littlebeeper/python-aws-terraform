import unittest
import uuid

from backend.config import DbConfig
from backend.db.model import Account

from backend.db.mongo_db_session import DbSessionMaker
from backend.db.mongo_setup import get_mongo_client
from backend.config_deps import app_config
from backend.scripts.test_helpers import setup_env


def create_internal_setup_client(db_config):
    admin_db_config = DbConfig(
        driver=db_config.driver,
        username='admin_user', # from local mongo's docker-compose.yml
        password=db_config.password,
        host=db_config.host,
        port=db_config.port,
        db_name='admin',
    )
    return get_mongo_client(db_config=admin_db_config)

class MongoDbTestBase(unittest.TestCase):

    def setUp(self) -> None:
        app_config.cache_clear()
        self.db_name = uuid.uuid4().hex
        setup_env(db_name=self.db_name)

        db_config = app_config().mongo_db_config
        self.assertEqual(self.db_name, db_config.db_name)

        self._setup_db_client = create_internal_setup_client(db_config)
        self._setup_db_client[self.db_name].command(
            'createUser',
            db_config.username,
            pwd=db_config.password,
            roles=[{'role': 'readWrite', 'db': self.db_name}])
        get_mongo_client.cache_clear()
        self.db_client = get_mongo_client()

        self.db = self.db_client[self.db_name]
        self.db_session_maker = DbSessionMaker(db=self.db_client.__getattr__(self.db_name), mongo_client=self.db_client)
        self.db_session = self.db_session_maker.__enter__()

    def tearDown(self) -> None:
        db_config = app_config().mongo_db_config
        self.db_session_maker.__exit__(None, None, None)

        self._setup_db_client[self.db_name].command(
            'dropUser',
            db_config.username,
        )
        self._setup_db_client.drop_database(self.db_name)
        self._setup_db_client.close()
        self.db_client.close()

    def create_account(self, account_id: str = 'acct_123'):
        with DbSessionMaker(self.db, self.db_client) as session:
            new_account = Account(id=account_id, name='test account')
            session.accounts_db.add_obj(new_account)
            return new_account
