import unittest
from tests.test_api_base import ApiTestBase


class SettingsApiTest(ApiTestBase):

    def setUp(self) -> None:
        super(SettingsApiTest, self).setUp()
        self.patch_auth()

    def tearDown(self) -> None:
        self.unpatched_auth()

    def test_get_settings(self):
        response = self.client.get('/settings')
        self.assertEqual(200, response.status_code, response.json())

    def test_update_settings(self):
        response = self.client.get('/settings')
        self.assertEqual(200, response.status_code, response.json())
        previous_settings = response.json()

        self.assertEqual('test account', previous_settings['name'])

        # capitalizable_hours_haircut: float
        # hours_in_work_week: int
        response = self.client.post('/settings', json=dict(
           name='new name',
        ))
        self.assertEqual(200, response.status_code, response.json())
        self.assertEqual('new name', response.json()['name'])

        response = self.client.get('/settings')
        self.assertEqual(200, response.status_code, response.json())
        self.assertEqual('new name', response.json()['name'])


if __name__ == '__main__':
    unittest.main()
