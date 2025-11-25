import logging

from dependency_injector.wiring import Provide
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.containers import Container
from ..core.exceptions.custom_exception import *
from app.security.security_config import SecurityConfig

from ..services.auth_service import AuthService


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        auth_service: AuthService = Provide[Container.auth_service],
        logger: logging.Logger = Provide[Container.logger],
        security_config: SecurityConfig = Provide[Container.security_config],
    ):
        super().__init__(app)
        self.auth_service = auth_service
        self.logger = logger
        self.security_config = security_config

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if self.security_config.is_auth_excluded_path(request.url.path, request.method):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            self.logger.error("Authorization header missing or invalid")
            raise UnauthorizedException()

        token = auth_header[7:].strip()
        if not token:
            self.logger.error("Bearer token is missing")
            raise InvalidTokenException()

        response = await call_next(request)
        return response
