from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from app.core.containers import Container
from ..services.health_service import HealthService


@inject
def health_controller(
    health_service: HealthService = Depends(Provide[Container.health_service]),
) -> APIRouter:
    router = APIRouter(prefix="/health", tags=["Health Check"])

    @router.get(
        "",
        summary="Health Check Endpoint",
        description="API 서버의 상태를 확인합니다.",
        include_in_schema=False,
    )
    def health_check():
        return health_service.check_health()

    @router.get(
        "/mysql",
        summary="MySQL Health Check Endpoint",
        description="MySQL 데이터베이스의 상태를 확인합니다.",
        include_in_schema=False,
    )
    def mysql_health_check():
        return health_service.check_health_mysql()

    @router.get(
        "/redis",
        summary="Redis Health Check Endpoint",
        description="Redis 캐시 서버의 상태를 확인합니다.",
        include_in_schema=False,
    )
    def redis_health_check():
        return health_service.check_health_redis()

    @router.get(
        "/s3",
        summary="S3 Health Check Endpoint",
        description="S3 스토리지 서비스의 상태를 확인합니다.",
        include_in_schema=False,
    )
    def s3_health_check():
        return health_service.check_health_s3()

    return router
