from propelauth_fastapi import init_auth, Auth
from backend.config_deps import app_config

config = app_config()
auth: Auth = init_auth(config.propel_auth_auth_url, config.propel_auth_api_key)

from propelauth_py import init_base_auth

base_auth = init_base_auth(config.propel_auth_auth_url, config.propel_auth_api_key)
