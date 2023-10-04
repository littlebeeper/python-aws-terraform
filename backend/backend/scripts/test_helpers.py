import os


def setup_env(
        api_domain='http://0.0.0.0:5001',
        website_domain='http://0.0.0.0:5002',
        propel_auth_auth_url='https://2912904.propelauthtest.com',
        propel_auth_api_key='dev/propelauth/api_key',
        nango_public_key='4c81f206-40c8-40a2-8e8d-c8df552ed722', # isolated from prod
        nango_secret_key='de2ff01c-5db6-47f1-8f23-ceb032d0bcc5', # isolated from prod
        react_build_path='backend/react_build_local',
        db_driver='mongodb',
        db_username='mongo',
        db_password='mongo',
        db_host='localhost',
        db_port='27017',
        db_name='admin',
        db_uri_params='',
        profiling='TRUE',
        resend_api_key='dev/resend/api_key',
        pagerduty_sns_topic_arn='pagerduty_sns_topic_arn',
        posthog_api_key='posthog/api_key',
):
    env_vars = {
        'SRV_ENV': 'TEST',
        'FLASK_ENV': 'testing',
        'API_DOMAIN': api_domain,
        'WEBSITE_DOMAIN': website_domain,
        'PROPEL_AUTH_AUTH_URL': propel_auth_auth_url,
        'SECRETS_MANAGER_KEY_PROPEL_AUTH_API_KEY': propel_auth_api_key,
        'NANGO_PUBLIC_KEY': nango_public_key,
        'NANGO_SECRET_KEY': nango_secret_key,
        'REACT_BUILD_PATH': react_build_path,
        'DB_DRIVER': db_driver,
        'DB_USERNAME': db_username,
        'DB_PASSWORD': db_password,
        'DB_HOST': db_host,
        'DB_PORT': db_port,
        'DB_NAME': db_name,
        'DB_URI_PARAMS': db_uri_params,
        'PROFILING': profiling,
        'SECRETS_MANAGER_KEY_RESEND_API_KEY': resend_api_key,
        'PAGER_DUTY_SNS_TOPIC_ARN': pagerduty_sns_topic_arn,
        'SECRETS_MANAGER_KEY_POSTHOG_API_KEY': posthog_api_key,
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    return env_vars
