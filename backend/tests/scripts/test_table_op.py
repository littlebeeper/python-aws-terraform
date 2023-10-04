from unittest.mock import patch
from backend.scripts.table_op import main, Action
from tests.mongo_db_test_base import MongoDbTestBase


class TestTableOp(MongoDbTestBase):

    def setUp(self) -> None:
        super(TestTableOp, self).setUp()
        # always bypass the "are you sure?" prompt
        self.p = patch('builtins.input', lambda _: 'y')
        self.p.start()

    def tearDown(self) -> None:
        self.p.stop()

    # create w/ lots of strange fields
    def test_creates_account(self):
        self.assertEqual(0, self.db_session.accounts_db.count())
        main('accounts', Action.CREATE, field_string='name=account name')
        self.assertEqual(1, self.db_session.accounts_db.count())

        main('accounts', Action.CREATE, field_string='name=a&created=2021-01-01T00:00:00Z')

    def test_reads_accounts(self):
        self.create_account(account_id='acct_234')
        self.create_account(account_id='acct_345')
        self.create_account(account_id='acct_456')

        # just ensure this doesn't break
        main('accounts', Action.READ)

    def test_updates_account(self):
        account = self.create_account(account_id='acct_234')
        self.assertEqual('test account', account.name)
        main('accounts', Action.UPDATE, query_string=f'id={account.id}', field_string='name=updated name')
        account = self.db_session.accounts_db.load_one(obj_id=account.id)
        self.assertEqual('updated name', account.name)

    def test_deletes_account(self):
        account = self.create_account(account_id='acct_234')
        self.assertEqual(1, self.db_session.accounts_db.count())
        main('accounts', Action.DELETE, query_string=f'id={account.id}')
        self.assertEqual(0, self.db_session.accounts_db.count())
