from ..health_service import HealthService
from ...core.base_response import BaseResponse
from ...core.mysql import MySQL
from ...core.redis import Redis
from ...core.s3 import S3Client
from ...core.exceptions.custom_exception import *


class HealthServiceImpl(HealthService):
    def __init__(
        self, logger, mysql: MySQL = None, redis: Redis = None, s3: S3Client = None
    ):
        self.logger = logger
        self.mysql = mysql
        self.redis = redis
        self.s3 = s3

    def check_health(self) -> dict:
        self.logger.info("Health check requested")
        return BaseResponse.success_response(
            message="서비스가 정상적으로 작동 중입니다.",
            data={"status": "healthy"},
        ).model_dump()

    def check_health_mysql(self):
        self.logger.info("MySQL health check requested")
        if self.mysql is None:
            self.logger.error("MySQL instance is not provided")
            raise DatabaseConnectionException("MySQL instance is not available")

        try:
            self.mysql.ping()
            return BaseResponse.success_response(
                message="MySQL 연결이 정상입니다.",
                data={"mysql_status": "connected"},
            ).model_dump()
        except Exception as e:
            raise DatabaseConnectionException("MySQL 연결에 실패했습니다.")

    def check_health_redis(self):
        self.logger.info("Redis health check requested")

        try:
            self.redis.ping()
            return BaseResponse.success_response(
                message="Redis 연결이 정상입니다.",
                data={"redis_status": "connected"},
            ).model_dump()
        except Exception as e:
            raise DatabaseConnectionException("Redis 연결에 실패했습니다.")

    def check_health_s3(self):
        self.logger.info("S3 health check requested")

        try:
            self.s3._is_bucket_accessible()
            return BaseResponse.success_response(
                message="S3 연결이 정상입니다.",
                data={"s3_status": "connected"},
            ).model_dump()
        except Exception as e:
            raise DatabaseConnectionException("S3 연결에 실패했습니다.")
