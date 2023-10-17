from enum import Enum
from dotenv import find_dotenv


class Environment(Enum):
    QA = 1 # deprecated
    STAGING = 2
    PRODUCTION = 3
    DEVELOPMENT = 4
    TEST = 5

    def __str__(self):
        return self.name.lower()


def resolve_env_file(env):
    env_file = '.env.{0}'.format(env)
    return find_dotenv(filename=env_file, raise_error_if_not_found=True)
