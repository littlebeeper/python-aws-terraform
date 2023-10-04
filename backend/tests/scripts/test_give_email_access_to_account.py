from backend.api.auth.permission import Permission
from backend.scripts.give_email_access_to_account import main
from tests.mongo_db_test_base import MongoDbTestBase


class TestGiveEmailAccessToAccount(MongoDbTestBase):

    def test_gives_email_access_to_account(self):
        account = self.create_account()
        self.assertEqual(0, self.db_session.user_account_access_db.count())
        main(account_id=account.id, raw_emails=['a@b.com'], permissions={Permission.WRITE})
        self.assertEqual(1, self.db_session.user_account_access_db.count())

        user_account_accesses = list(self.db_session.user_account_access_db.query({'email': 'a@b.com'}))
        self.assertEqual(1, len(user_account_accesses))
        use_account_access = user_account_accesses[0]
        self.assertEqual(account.id, use_account_access.account_id)
        self.assertEqual('a@b.com', use_account_access.email)

    def test_dedupes_emails(self):
        account = self.create_account()
        self.assertEqual(0, self.db_session.user_account_access_db.count())
        main(account_id=account.id, raw_emails=['a@b.com', 'a@b.com'], permissions={Permission.WRITE})
        self.assertEqual(1, self.db_session.user_account_access_db.count())

        user_account_accesses = list(self.db_session.user_account_access_db.query({'email': 'a@b.com'}))
        self.assertEqual(1, len(user_account_accesses))
        use_account_access = user_account_accesses[0]
        self.assertEqual(account.id, use_account_access.account_id)
        self.assertEqual('a@b.com', use_account_access.email)

    def test_dedupes_across_runs(self):
        account = self.create_account()
        self.assertEqual(0, self.db_session.user_account_access_db.count())
        main(account_id=account.id, raw_emails=['a@b.com'], permissions={Permission.WRITE})
        self.assertEqual(1, self.db_session.user_account_access_db.count())

        main(account_id=account.id, raw_emails=['a@b.com'], permissions={Permission.WRITE})
        self.assertEqual(1, self.db_session.user_account_access_db.count())

        user_account_accesses = list(self.db_session.user_account_access_db.query({'email': 'a@b.com'}))
        self.assertEqual(1, len(user_account_accesses))
        use_account_access = user_account_accesses[0]
        self.assertEqual(account.id, use_account_access.account_id)
        self.assertEqual('a@b.com', use_account_access.email)

    def test_validates_emails(self):
        account = self.create_account()
        self.assertRaises(ValueError, lambda: main(account_id=account.id, raw_emails=['a@bcom'], permissions={Permission.WRITE}))
        self.assertRaises(ValueError, lambda: main(account_id=account.id, raw_emails=['@@b.com'], permissions={Permission.WRITE}))
        self.assertRaises(ValueError, lambda: main(account_id=account.id, raw_emails=['@bcom'], permissions={Permission.WRITE}))
