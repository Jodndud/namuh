from fastapi import FastAPI

from .cors_config_middleware import CORSConfigMiddleware
from .logging_middleware import LoggingMiddleware
from .jwt_middleware import JWTMiddleware


class MiddlewareConfig:
    @staticmethod
    def configure_middlewares(app: FastAPI) -> None:
        settings = app.container.settings()
        logger = app.container.logger()

        app.add_middleware(LoggingMiddleware, logger=logger)
        app.add_middleware(CORSConfigMiddleware, settings=settings)
        app.add_middleware(JWTMiddleware, logger=logger)
