from uvicorn.config import LOGGING_CONFIG
from copy import deepcopy


def build_webserver_log_config(prefix):
    log_config = deepcopy(LOGGING_CONFIG)
    log_config['formatters']['default']['fmt'] = "[{0}]{1}".format(prefix, log_config['formatters']['default']['fmt'])
    return log_config