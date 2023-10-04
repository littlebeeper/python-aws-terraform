from propelauth_fastapi import Auth, User

class FakeUser(User):
    def __init__(self, user_id, email):
        super().__init__(user_id=user_id, org_id_to_org_member_info={}, email=email)

class MockAuth:

    def __init__(self, user_id='mock_user_id', email='example@mogara.com'):
        self.user_id = user_id
        self.email = email
        self.require_user = lambda : FakeUser(user_id, email)

    def fetch_user_metadata_by_user_id(self, user_id, include_orgs=False):
        assert user_id == self.user_id, f'Unexpected user_id: {user_id}'
        assert not include_orgs, 'Unexpected include_orgs'
        return {
            'email': self.email,
        }

    def validate_access_token_and_get_user(self, access_token):
        return FakeUser(self.user_id, self.email)
