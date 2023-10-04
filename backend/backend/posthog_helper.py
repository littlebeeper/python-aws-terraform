from posthog import Posthog

from backend.config_deps import app_config

# The personal API key is necessary only if you want to use local evaluation of feature flags.
config = app_config()
posthog = Posthog(config.posthog_api_key, host='https://app.posthog.com')

def is_flag_enabled(flag_name: str, account_id: str) -> bool:
    return posthog.is_feature_enabled(flag_name, account_id)
