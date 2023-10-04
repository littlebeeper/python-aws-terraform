import unittest
from tests.test_api_base import ApiTestBase

class ApiTest(ApiTestBase):

    def setUp(self) -> None:
        super(ApiTest, self).setUp()
        self.patch_auth()

    def tearDown(self) -> None:
        self.unpatched_auth()

    def test_ping_works(self):
        response = self.client.get('/ping',)
        self.assertEqual(200, response.status_code, response)
        self.assertEqual('Ping received!', response.text)
        self.client

    def test_session_works(self):
        response = self.client.get('/session')
        self.assertEqual(200, response.status_code, response.json())
        self.assertEqual(self.account_id, response.json()['account_id'])
        self.assertEqual(self.email, response.json()['email'])
        self.assertEqual(self.user_id, response.json()['user_id'])

if __name__ == '__main__':
    unittest.main()
