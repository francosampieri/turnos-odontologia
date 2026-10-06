from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

import logging

from app.api.routers import health
from app.core.config import Settings

logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"


def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def _unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    logger.exception("Excepción no controlada")
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


def create_app(settings: Settings) -> FastAPI:
    production = settings.env == "production"
    app = FastAPI(
        title="Turnos Odontología API",
        docs_url=None if production else "/docs",
        openapi_url=None if production else "/openapi.json",
        redoc_url=None if production else "/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
    app.include_router(health.router, prefix=API_PREFIX)
    return app


app = create_app(Settings())