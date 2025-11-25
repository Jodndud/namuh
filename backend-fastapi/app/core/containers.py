import logging

from dependency_injector import containers, providers

from app.core.load_settings import load_settings
from app.core import mysql as mysql_module
from app.core.mysql import MySQL as MySQLClient
from app.core.redis import Redis
from app.core.s3 import S3Client
from app.core.mqtt import MQTTClient


from app.security.jwt_provider import JwtProvider
from app.security.security_config import SecurityConfig


from app.services.implementation.health_service_impl import HealthServiceImpl
from app.services.implementation.auth_service_impl import AuthServiceImpl
from app.services.implementation.stt_tts_service_impl import SttTtsServiceImpl
from app.services.implementation.s3_service_impl import S3ServiceImpl
from app.services.implementation.mqtt_service_impl import MQTTServiceImpl


from app.repositories.media_repository import MediaRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.controllers.health_controller",
            "app.controllers.stt_tts_controller",
            "app.controllers.s3_controller",
            "app.controllers.mqtt_controller",
            "app.middlewares.jwt_middleware",
            "app.middlewares.logging_middleware",
        ]
    )
    config = providers.Configuration()
    settings = providers.Singleton(load_settings)
    logger = providers.Singleton(logging.getLogger, name="buriburi fastapi")
    version = providers.Object(settings().version)
    docs_url = providers.Object(f"/{settings().docs_url}")
    redoc_url = providers.Object(f"/{settings().redoc_url}")
    openapi_url = providers.Object(f"/{settings().openapi_url}")

    # Database
    mysql_engine = providers.Singleton(mysql_module.init_mysql_pool, settings=settings)
    mysql = providers.Singleton(MySQLClient, engine=mysql_engine)
    redis = providers.Singleton(Redis, settings=settings)
    s3_client = providers.Singleton(S3Client, settings=settings, logger=logger)

    # MQTT Client
    mqtt_client = providers.Singleton(
        MQTTClient, settings=settings, logger=logger, redis=redis
    )

    # Session Factory
    db_session = providers.Factory(
        lambda mysql_instance: mysql_instance.get_session(), mysql_instance=mysql
    )

    # Repositories
    media_repository = providers.Factory(
        MediaRepository,
        session=db_session,
    )

    # Services
    jwt_service = providers.Singleton(JwtProvider, settings=settings)
    health_service = providers.Singleton(
        HealthServiceImpl,
        logger=logger,
        mysql=mysql,
        redis=redis,
        s3=s3_client,
    )
    stt_tts_service = providers.Singleton(
        SttTtsServiceImpl,
        settings=settings,
        logger=logger,
        mqtt_client=mqtt_client,
    )
    s3_service = providers.Singleton(
        S3ServiceImpl,
        s3_client=s3_client,
        logger=logger,
        media_repository=media_repository,
    )
    mqtt_service = providers.Singleton(
        MQTTServiceImpl,
        mqtt_client=mqtt_client,
        logger=logger,
        redis=redis,
        settings=settings,
    )

    auth_service = providers.Singleton(
        AuthServiceImpl,
        jwt_provider=jwt_service,
        logger=logger,
    )

    security_config = providers.Singleton(SecurityConfig)


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])
    service = container.health_service()
