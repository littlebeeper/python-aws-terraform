from backend.scripts.account_create import main
from tests.mongo_db_test_base import MongoDbTestBase


class TestAccountCreate(MongoDbTestBase):

    def test_creates_account(self):
        self.assertEqual(0, self.db_session.accounts_db.count())
        new_account_id = main(name='test account')
        self.assertEqual(1, self.db_session.accounts_db.count())

        account = self.db_session.accounts_db.load_one(obj_id=new_account_id)
        self.assertEqual(new_account_id, account.id)
        self.assertEqual('test account', account.name)
        self.assertIsNotNone(account.created)

    def test_prevents_creating_an_account_with_same_name(self):
        self.assertEqual(0, self.db_session.accounts_db.count())
        main(name='test account')
        self.assertEqual(1, self.db_session.accounts_db.count())
        with self.assertRaises(Exception):
            main(name='test account')
        self.assertEqual(1, self.db_session.accounts_db.count())
