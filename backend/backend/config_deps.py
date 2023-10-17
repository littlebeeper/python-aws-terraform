import functools
import logging

from backend.config import Config, DbConfig
from backend.config_helpers import resolve, resolve_secret
from backend.env import Environment


@functools.cache
def app_config(
        env: str = None,
        api_domain=None,
        website_domain=None,
        propel_auth_auth_url=None,
        propel_auth_api_key=None,
        nango_public_key=None,
        nango_secret_key=None,
        db_driver=None,
        db_username=None,
        db_password=None,
        db_host=None,
        db_port=None,
        db_name=None,
        db_uri_params=None,
        profiling=False,
        resend_api_key=None,
        pagerduty_sns_topic_arn=None,
        posthog_api_key=None,
):
    env: Environment = Environment[resolve('SRV_ENV', override=env).upper()]

    # log aws credentials if in development
    if env == Environment.DEVELOPMENT:
        # load them from "/root/.aws/credentials"
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()

        if credentials is None:
            logging.info("credentials is None")
            # print the contents of the file
            with open("/root/.aws/credentials", "r") as f:
                logging.info("contents of /root/.aws/credentials:")
                logging.info(f.read())
        else:
            logging.info("credentials.access_key: " + credentials.access_key)
            logging.info("credentials.secret_key: " + credentials.secret_key)


    # remove STAGING
    if env == Environment.DEVELOPMENT or env == Environment.STAGING:
        print("loading .env." + env.name.lower())
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(f'.env.{env}'))
        # print all envirnoment variables
        import os
        print("all environment variables:")
        print(os.environ)

    return Config(
        env=env,
        debug=resolve('DEBUG', default='FALSE').upper() == 'TRUE',

        api_domain=resolve('API_DOMAIN', override=api_domain),
        website_domain=resolve('WEBSITE_DOMAIN', override=website_domain),

        propel_auth_auth_url=resolve('PROPEL_AUTH_AUTH_URL', override=propel_auth_auth_url),
        propel_auth_api_key=resolve_secret(env, 'SECRETS_MANAGER_KEY_PROPEL_AUTH_API_KEY', override=propel_auth_api_key),

        nango_public_key=resolve('NANGO_PUBLIC_KEY', override=nango_public_key),
        nango_secret_key=resolve_secret(env, 'SECRETS_MANAGER_KEY_NANGO_SECRET_KEY', override=nango_secret_key),

        mongo_db_config=DbConfig(
            driver=resolve('DB_DRIVER', override=db_driver),
            username=resolve('DB_USERNAME', override=db_username),
            password=resolve_secret(env, 'SECRETS_MANAGER_KEY_DB_PASSWORD', override=db_password),
            host=resolve('DB_HOST', override=db_host),
            port=resolve('DB_PORT', override=db_port),
            db_name=resolve('DB_NAME', override=db_name),
            db_uri_params=resolve('DB_URI_PARAMS', override=db_uri_params),
        ),
        profiling=resolve('PROFILE', default='FALSE', override=profiling).upper() == 'TRUE',
        resend_api_key=resolve_secret(env, 'SECRETS_MANAGER_KEY_RESEND_API_KEY', override=resend_api_key),
        pagerduty_sns_topic_arn=resolve('PAGER_DUTY_SNS_TOPIC_ARN', override=pagerduty_sns_topic_arn),
        posthog_api_key=resolve('SECRETS_MANAGER_KEY_POSTHOG_API_KEY', override=posthog_api_key),
    )
