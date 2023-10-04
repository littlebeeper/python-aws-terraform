import unittest
from backend.config_deps import app_config
from backend.scripts.test_helpers import setup_env


class SimpleEnvTestBase(unittest.TestCase):

    def setUp(self) -> None:
        app_config.cache_clear()
        setup_env()

    def tearDown(self) -> None:
        pass
