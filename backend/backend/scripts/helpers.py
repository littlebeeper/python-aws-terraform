import os

from backend.env import Environment
from dotenv import find_dotenv, load_dotenv
from email_validator import validate_email, EmailNotValidError

def setup_env(env, cwd_depth_from_backend_root=2, allow_test_env=False):
    if env == Environment.TEST:
        from backend.scripts.test_helpers import setup_env as setup_test_env
        if not allow_test_env:
            raise Exception('TEST env is not allowed, if you really want to use it, set allow_test_env=True')
        setup_test_env()
        return

    os.environ['SRV_ENV'] = str(env)
    load_env_file(env, cwd_depth_from_backend_root=cwd_depth_from_backend_root)


def load_env_file(env, cwd_depth_from_backend_root=2):
    prefix = '../' * cwd_depth_from_backend_root
    env_file_path = prefix + '.env.{0}'.format(env)
    print(f'current working directory: {os.getcwd()}')
    print('Loading env file: {0}'.format(env_file_path))
    assert os.path.exists(env_file_path), f"env file {env_file_path} does not exist"
    load_dotenv(find_dotenv(filename=env_file_path, raise_error_if_not_found=True))

def validate_and_normalize_email(email):
    try:
        validation = validate_email(email, check_deliverability=False)
        return validation.email
    except EmailNotValidError as e:
        raise ValueError(f'Invalid email: {email}')