from enum import Enum
from dotenv import find_dotenv


class Environment(Enum):
    QA = 1
    PRODUCTION = 2
    DEVELOPMENT = 3
    TEST = 4

    def __str__(self):
        return self.name.lower()

    def app_name(self):
        return "mogara-{0}".format(self.name.lower())


def resolve_env_file(env):
    env_file = '.env.{0}'.format(env)
    return find_dotenv(filename=env_file, raise_error_if_not_found=True)
