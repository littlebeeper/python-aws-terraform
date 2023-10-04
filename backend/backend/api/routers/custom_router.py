from propelauth_py.user import User
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

import json
import logging
from pprint import PrettyPrinter


from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.routing import APIRoute

from backend.api.auth.integration import base_auth
from backend.config_deps import app_config
from backend.db.mongo_db_session import DbSessionMaker
from backend.db.mongo_setup import get_db, get_mongo_client
from backend.metrics import metrics_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pp = PrettyPrinter(indent=2)

def pretty_json_string(json_data: str) -> str:
    json_object = json.loads(json_data)
    return json.dumps(json_object, indent=2)


def get_account_id_and_email(request: Request) -> (Optional[str], Optional[str]):
    auth_token = request.headers.get('Authorization', None)
    if auth_token is None:
        return None, None
    user: User = base_auth.validate_access_token_and_get_user(auth_token)
    with DbSessionMaker(get_db(), get_mongo_client()) as dbs:
        account_id = dbs.user_account_access_db.get_account_id(user.email)

    return account_id, user.email


def canonical_api_line(request: Request, response: Response, req_body: bytes, res_body: bytes) -> None:
    metrics_client().incr(str(response.status_code))
    account_id, email = get_account_id_and_email(request)
    try:
        log_data = {
            'type': 'API_REQUEST',
            'method': request.method,
            'path': request.url.path,
            'status': response.status_code,
            'account_id': account_id,
            'email': email,
            'query_params': json.dumps(dict(request.query_params)),
            'req_body': req_body.decode('utf-8'),
            'res_body': res_body.decode('utf-8'),
        }
        logging.info(json.dumps(log_data))
    except Exception as e:
        logger.error(f'Error logging canonical api line: {e}')

def log_debug_info(req_body: bytes, res_body: bytes, response_headers, response_status: int):
    logging.info('Request/Response Info:')
    if len(req_body) > 0:
        logging.info(f"Request: {req_body.decode()}")
    logging.info(f'Response:\n{pretty_json_string(res_body.decode())},\n{pp.pformat(response_headers)}')
    metrics_client().incr(str(response_status))

class SrvRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            response = await original_route_handler(request)

            config = app_config()

            if isinstance(response, StreamingResponse):
                res_body: bytes = b''
                async for item in response.body_iterator:
                    res_body += item.encode('utf-8')

                if config.debug:
                    task = BackgroundTask(log_debug_info, req_body, res_body, response.headers, response.status_code)
                else:
                    task = BackgroundTask(canonical_api_line, request, response, req_body, res_body)

                return Response(content=res_body, status_code=response.status_code,
                                headers=dict(response.headers), media_type=response.media_type, background=task)
            else:
                res_body = response.body
                if config.debug:
                    response.background = BackgroundTask(log_debug_info, req_body, res_body, response.headers, response.status_code)
                else:
                    response.background = BackgroundTask(canonical_api_line, request, response, req_body, res_body)
                return response

        return custom_route_handler
