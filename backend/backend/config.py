from typing import Optional

from pydantic.main import BaseModel

from backend.env import Environment


class DbConfig(BaseModel):
    driver: str
    username: str
    password: str
    host: str
    port: Optional[str]
    db_name: str
    ssl_mode: Optional[str]  # disable, allow, prefer, require, verify-ca, verify-full
    uri_params: str = ''

    class Config:
        frozen = True


class Config(BaseModel):
    env: Environment
    debug: bool
    flask_env: str

    api_domain: str
    website_domain: str

    propel_auth_auth_url: str
    propel_auth_api_key: str

    nango_public_key: str
    nango_secret_key: str

    mongo_db_config: DbConfig

    profiling: bool = False

    resend_api_key: str

    pagerduty_sns_topic_arn: str

    posthog_api_key: str

    class Config:
        frozen = True

    def is_testing(self):
        return self.env == Environment.TEST

    def is_testing_or_development(self):
        return self.env in [Environment.TEST, Environment.DEVELOPMENT]

    def has_deployed_infrastructure(self):
        return self.env in [Environment.PRODUCTION, Environment.QA]
