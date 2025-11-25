import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.controllers import ControllerConfig
from app.core.containers import Container
from app.middlewares import MiddlewareConfig

from app.core.exceptions.base_exception import BaseException
from app.core.exceptions.exception_handler import (
    app_exception_handler,
    generic_exception_handler,
)
from contextlib import asynccontextmanager


def setup_openapi(app: FastAPI, security_config):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            description=app.description,
            summary=app.summary,
            version=app.container.version(),
            servers=[{"url": "/fastapi"}],
            routes=app.routes,
        )

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "Bearer",
                "bearerFormat": "JWT",
                "description": "JWT 토큰을 입력하세요.",
            }
        }

        for path, path_item in openapi_schema.get("paths", {}).items():
            for method in list(path_item.keys()):
                if not security_config.is_auth_excluded_path(path, method.upper()):
                    path_item[method]["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi_schema = None
    app.openapi = custom_openapi


def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    container = Container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mqtt_client = container.mqtt_client()

        try:
            await mqtt_client.start()
        except Exception as e:
            logger = container.logger()
            logger.warning(f"MQTT 클라이언트 시작 중 오류 발생: {e}")

        yield

        await mqtt_client.stop()

    app = FastAPI(
        title="Buriburi - FastAPI",
        summary="Buriburi FastAPI 서버입니다.",
        description="나는 언제나 강한 자의 편이다. - 부리부리몬",
        docs_url=container.docs_url(),
        redoc_url=container.redoc_url(),
        openapi_url=container.openapi_url(),
        root_path="/fastapi",
        lifespan=lifespan,
    )

    app.container = container

    security_config = container.security_config()

    MiddlewareConfig.configure_middlewares(app)

    for router in ControllerConfig.get_all_routers():
        app.include_router(router, prefix=f"/{container.version()}")

    setup_openapi(app, security_config)

    # 예외 핸들러 등록
    app.add_exception_handler(BaseException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
