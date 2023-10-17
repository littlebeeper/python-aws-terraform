#!/usr/bin/env python

import os
import uvicorn

from backend.api.app import init_app
from backend.config_deps import app_config
from backend.log_utils import build_webserver_log_config

app = init_app()
app.debug = True

if __name__ == "__main__":
    config = app_config()
    port = int(os.environ.get('PORT', 5001))
    uvicorn.run(
        app="backend.backend_fargate:app",
        host='localhost',
        port=port,
        reload=True,
        log_config=build_webserver_log_config(prefix='API'))
