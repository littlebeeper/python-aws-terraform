from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from backend.api.routers.custom_router import SrvRoute

router = APIRouter(route_class=SrvRoute)


@router.get('/health', tags=['health'])
async def health():
    return {'status': 'ok'}


@router.get('/ping', tags=['health'])
async def ping():
    return PlainTextResponse(content='Ping received!')

@router.get('/status_test', tags=['health'])
async def test500(status: int = 500):
    return PlainTextResponse(content=f"Status test: {status}", status_code=status)
