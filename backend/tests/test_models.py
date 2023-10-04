import unittest

from backend.api.auth.permission import Permission
from backend.db.model import Account, UserAccountAccess

from tests.mongo_db_test_base import MongoDbTestBase


class TestModels(MongoDbTestBase):

    def test_empty(self):
        pass

    def assert_count(self, expected_count, lst):
        self.assertEqual(expected_count, len(list(lst)))

    def assert_serialize_deserialize(self, db, new_obj):
        self.assert_count(0, db.load_all())
        db.add_obj(new_obj)

        self.assert_count(1, db.load_all())
        self.assertEqual(new_obj, db.load_one(obj_id=new_obj.id))

    def test_create_account(self):
        new_account = Account(name='name')
        self.assert_serialize_deserialize(self.db_session.accounts_db, new_obj=new_account)

    def test_fails_when_attempting_to_add_incorrect_model_type(self):
        user_account_access = UserAccountAccess(
            email='',
            account_id='',
            permissions=[],
        )

        with self.assertRaises(TypeError) as cm:
            self.db_session.accounts_db.add_obj(user_account_access)
        self.assertEqual("Expected Account but got UserAccountAccess obj", str(cm.exception))

        self.db_session.user_account_access_db.add_obj(user_account_access)

        with self.assertRaises(TypeError) as cm:
            self.db_session.accounts_db.update_obj(user_account_access)
        self.assertEqual("Expected Account but got UserAccountAccess obj", str(cm.exception))

    def test_create_user_account_access(self):
        new_user_account_access = UserAccountAccess(
            email='example@example.com',
            account_id='acct_123',
            permissions=[Permission.WRITE],
        )
        self.assert_serialize_deserialize(self.db_session.user_account_access_db, new_obj=new_user_account_access)

    def test_deletion(self):
        new_user_account_access = UserAccountAccess(
            email='example@example.com',
            account_id='acct_123',
            permissions=[Permission.WRITE],
        )

        self.assert_count(0, self.db_session.user_account_access_db.load_all())

        self.db_session.user_account_access_db.add_obj(new_user_account_access)
        self.assert_count(1, self.db_session.user_account_access_db.load_all())

        self.db_session.user_account_access_db.delete_many(obj_ids=[new_user_account_access.id], account_id='acct_123')
        self.assert_count(0, self.db_session.user_account_access_db.load_all())

    # Note: Can't test this via the api tests b/c of how we mock auth
    def test_user_seller_access_db_load_by_email(self):
        new_user_account_access = UserAccountAccess(
            email='present@example.com',
            account_id='acct_123',
            permissions=[Permission.WRITE],
        )

        self.db_session.user_account_access_db.add_obj(new_user_account_access)
        self.assertEqual('acct_123',
                         self.db_session.user_account_access_db.get_account_id(email='present@example.com'))

        self.assertEqual(None,
                         self.db_session.user_account_access_db.get_account_id(email='notpresent@example.com'))

if __name__ == '__main__':
    unittest.main()
