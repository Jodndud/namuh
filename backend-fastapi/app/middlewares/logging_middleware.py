import logging
import time

from dependency_injector.wiring import Provide, inject
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.containers import Container


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: logging.Logger = Provide[Container.logger]):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        self.logger.info(
            f"Request: {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)

            process_time = time.time() - start_time
            self.logger.info(f"Response: {response.status_code} - {process_time: .4f}s")

            return response
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(f"Error processing request: {e} - {process_time: .4f}s")
            raise e
