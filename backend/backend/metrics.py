import functools

from statsd import StatsClient

from backend.config import Config
from backend.config_deps import app_config

@functools.cache
def metrics_client():
    config: Config = app_config()
    return StatsClient(prefix=config.env.name.lower())
