import logging

from fastapi import FastAPI
from fastapi.routing import APIRoute

from backend.config import Config

logger = logging.getLogger(__name__)

import sentry_sdk

from backend.api.cors import CORSScopingMiddleware
from backend.api.routers import health, session, settings
from backend.config_deps import app_config


def init_app():
    """Initialize the core application."""
    config: Config = app_config()

    is_testing = config.is_testing()

    if not is_testing:
        sentry_sdk.init(
            dsn="https://22a2e7e1b79a4e5faecfb500692108b6@o4505549420691456.ingest.sentry.io/4505549425606656",
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=1.0,
            environment=str(config.env),
        )

    def custom_generate_unique_id(route: APIRoute):
        return f"{route.name}"

    app = FastAPI(title="srv", debug=is_testing, generate_unique_id_function=custom_generate_unique_id)

    app.add_middleware(
        CORSScopingMiddleware,
        config=config,
        allow_origins=[
            config.website_domain,
        ],
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
        max_age=5,  # the default https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
    )

    app.get("/test")(lambda: {"message": "Welcome to the srv API!"})

    app.include_router(session.router, prefix='/session')
    app.include_router(settings.router, prefix='/settings')
    app.include_router(health.router)

    return app
