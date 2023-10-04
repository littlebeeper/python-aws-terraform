import logging
from datetime import datetime, timezone

import backoff
import requests
from dateutil import parser
from pydantic import BaseModel

from backend.config_deps import app_config

GITHUB_PROVIDER_CONFIG_KEY = 'github'
JIRA_PROVIDER_CONFIG_KEY = 'jira'
BOX_PROVIDER_CONFIG_KEY = 'box'
ASANA_PROVIDER_CONFIG_KEY = 'asana'
SLACK_PROVIDER_CONFIG_KEY = 'slack'

class OauthInfo(BaseModel):
    provider: str
    account_id: str
    expired: bool
    access_token: str

# TODO: cache oauth info till the smaller of expiration time or 1 hour
@backoff.on_exception(backoff.expo, Exception, max_tries=3) # nango has a cold start failure problem
def get_oauth_info(connection_id: str, provider: str) -> OauthInfo:
    config = app_config()
    nango_secret_key = config.nango_secret_key

    # TODO remove dev check here. It's only for temporary testing
    if app_config().is_testing() or app_config().is_testing_or_development():
        connection_id = 'test'

    # print(f'get_oauth_info: {connection_id}, {provider}, {nango_secret_key}')

    response = requests.get(
        f'https://api.nango.dev/connection/{connection_id}?provider_config_key={provider}',
        headers={"Authorization": f"Bearer {nango_secret_key}"})

    if response.status_code != 200:
        logging.error(f"get_oauth_info failed with status code {response.json()}")
        raise Exception(f"get_oauth_info failed with status code {response.json()}")

    if response.json().get('credentials') is None:
        logging.error(f"get_oauth_info failed with response {response.json()}")
        raise Exception(f"get_oauth_info failed with response {response.json()}")

    expired = response.json().get('credentials').get('expires_at') is not None and \
        parser.isoparse(response.json().get('credentials').get('expires_at')) < datetime.now(timezone.utc)

    return OauthInfo(
        provider=provider,
        account_id=connection_id,
        expired=expired,
        access_token=response.json().get('credentials').get('access_token')
    )

def is_oauth_active(account_id, provider: str):
    try:
        oauth_info = get_oauth_info(account_id, provider)

        # pull the expired datetime with dateutil
        if oauth_info.expired:
            return False

        return True
    except Exception as e:
        logging.error(f"get_oauth_info failed with exception {e}")
        return False
