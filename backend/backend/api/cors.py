import logging

from starlette.middleware.cors import CORSMiddleware

# We need to use a custom middleware to manage CORS for public and private endpoints
# Using FastAPI's built-in CORS middleware is not enough
# Using FastAPI's sub-apps is not enough either (because it breaks some core assumptions of our Supertokens integration)
# Specifically:
# - supertokens gives you a middleware that you can add to your app
# - This middleware does the correct cookie handling to ensure authentication works
class CORSScopingMiddleware:
    def __init__(self, app, config, allow_origins, allow_methods, allow_headers, allow_credentials, max_age):
        self.cors_for_private_endpoints = CORSMiddleware(
            app,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            max_age=max_age
        )

        self.cors_for_public_endpoints = CORSMiddleware(
            app,
            allow_origins=['*'],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=6,
        )
        self.app = app
        self.config = config

    async def __call__(self, scope, receive, send):
        # https://www.starlette.io/middleware/#writing-pure-asgi-middleware
        if scope['type'] == 'http':
            if scope['path'].startswith('/health') or \
                scope['path'].startswith('/ping'):
                return await self.cors_for_public_endpoints(scope, receive, send)
            else:
                return await self.cors_for_private_endpoints(scope, receive, send)
        else:
            return await self.app(scope, receive, send)
