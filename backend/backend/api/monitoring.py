import pydantic

from backend.api.server_timing_middleware import ServerTimingMiddleware

from backend.api.request_context_deps import get_user_by_id, get_mongo_db_session

from fastapi import FastAPI
import fastapi

from backend.config import Config


def add_monitoring_middleware(app: FastAPI, config: Config):
    if config.profiling:
        app.add_middleware(ServerTimingMiddleware, calls_to_track={
            "1deps": (fastapi.routing.solve_dependencies,),
            "1deps_db_session": (get_mongo_db_session,),
            "2main": (fastapi.routing.run_endpoint_function,),
            "2.3.1get_user_by_id": (get_user_by_id,),
            "3valid": (pydantic.fields.ModelField.validate,),
            "4encode": (fastapi.e.encoders.jsonable_encoder,),
            "4render": (
                fastapi.responses.JSONResponse.render,
                fastapi.responses.ORJSONResponse.render,
            ),
        })
