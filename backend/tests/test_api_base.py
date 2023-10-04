import unittest
from copy import copy
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api.auth.permission import Permission
from backend.db.model import Account, UserAccountAccess
from backend.db.model.builder import Builder
from tests.mock_auth import MockAuth, FakeUser
from tests.mongo_db_test_base import MongoDbTestBase


USER_ID = 'mock_user_id'
TEST_EMAIl = 'example@mogara.com'


class ApiTestBase(MongoDbTestBase):

    def setUp(self) -> None:
        super(ApiTestBase, self).setUp()

        from backend.api.app import init_app

        self.app = init_app()

        self.user_id = USER_ID
        self.email = TEST_EMAIl

        from backend.api.auth.integration import auth
        self.app.dependency_overrides[auth.require_user] = lambda: FakeUser(user_id=self.user_id, email=self.email)

        self.client = TestClient(self.app)

        self.patches = None

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}

    def patch_auth(self, account_id='acct_123'):
        self.account_id = account_id
        self.create_account(account_id=account_id)
        self.db_session.user_account_access_db.add_obj(
            UserAccountAccess(
                email=self.email,
                account_id=self.account_id,
                permissions=[Permission.WRITE, Permission.READ],
            )
        )

        self.patches = [
            patch(
                'backend.api.routers.custom_router.base_auth',
                MockAuth(email=self.email),
            ),
        ]
        for i, p in enumerate(self.patches):
            p.start()
    def unpatched_auth(self):
        if self.patches is not None:
            for p in self.patches:
                p.stop()
            self.patches = None

    def assert_auth_patched(self):
        return self.patches is not None

    def assert_auth_not_patched(self):
        return self.patches is None

    def get_account(self):
        return self.db_session.accounts_db.load_one(self.account_id)

    def set_user_permissions(self, permissions: list[Permission]):
        user_account_access = self.db_session.user_account_access_db.query_one(dict(email=self.email))
        user_account_access_builder = Builder(UserAccountAccess, existing_model=user_account_access)
        user_account_access_builder.permissions = permissions
        self.db_session.user_account_access_db.update_obj(user_account_access_builder.build())
        self.user_permissions = permissions

    def set_gate(self, gate_name: str, enabled: bool):
        account = self.get_account()
        account_builder = Builder(Account, existing_model=account)
        existing_gates = copy(account.gates)
        existing_gates[gate_name] = enabled
        account_builder.gates = existing_gates
        self.db_session.accounts_db.update_obj(account_builder.build())


if __name__ == '__main__':
    unittest.main()
