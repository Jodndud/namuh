import os

from dotenv import load_dotenv
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="Buriburi API", description="애플리케이션 이름")
    profile: str = Field(default="local", description="실행 환경")

    cors_allow_origins: str = Field(
        default="", description="CORS 허용 오리진 (쉼표로 구분)"
    )

    @property
    def cors_allow_origins_list(self) -> list[str]:
        if not self.cors_allow_origins:
            return []
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]

    # JWT 설정
    jwt_secret_key: str = Field(..., description="JWT Secret Key")
    jwt_algorithm: str = Field(..., description="JWT 알고리즘")

    # FastAPI 설정
    version: str = Field(default="v1", description="API 버전")
    docs_url: str = Field(default="docs", description="Swagger UI 문서 경로")
    redoc_url: str = Field(default="redoc", description="ReDoc 문서 경로")
    openapi_url: str = Field(default="openapi.json", description="OpenAPI 스키마 경로")

    # SSAFY GMS
    gms_api_key: str = Field(..., description="SSAFY GMS API Key")
    gms_api_url: str = Field(..., description="SSAFY GMS API URL")

    # MySQL 설정
    mysql_url: str = Field(..., description="MySQL 접속 URL")
    mysql_username: str = Field(..., description="MySQL 사용자 이름")
    mysql_password: str = Field(..., description="MySQL 비밀번호")
    mysql_db_name: str = Field(..., description="MySQL 데이터베이스 이름")
    mysql_port: int = Field(..., description="MySQL 포트 번호")

    # Redis 설정
    redis_host: str = Field(..., description="Redis 호스트")
    redis_port: int = Field(..., description="Redis 포트")
    redis_password: str = Field(..., description="Redis 비밀번호")
    redis_topic_key: str = Field(..., description="Redis key")

    # S3 설정
    s3_access_key: str = Field(..., description="S3 액세스 키")
    s3_secret_key: str = Field(..., description="S3 비밀 키")
    s3_region_static: str = Field(..., description="S3 리전")
    s3_bucket: str = Field(..., description="S3 버킷 이름")

    # OpenVidu 설정
    openvidu_url: str = Field(..., description="OpenVidu 서버 URL")
    openvidu_secret: str = Field(..., description="OpenVidu 시크릿 키")
    openvidu_session_prefix: str = Field(..., description="OpenVidu 세션 접두사")

    # MQTT 설정
    mqtt_host: str = Field(..., description="MQTT 브로커 URL")
    mqtt_port: int = Field(..., description="MQTT 브로커 포트")
    mqtt_username: str = Field(..., description="MQTT 사용자 이름")
    mqtt_password: str = Field(..., description="MQTT 비밀번호")
    mqtt_keepalive: int = Field(default=60, description="MQTT Keepalive 시간")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "APP_",
        "extra": "ignore",
    }


def load_settings() -> Settings:
    try:
        load_dotenv(override=False)

        profile = os.getenv("APP_PROFILE", "local").lower()

        prof_env_file = f".env.{profile}"
        if os.path.exists(prof_env_file):
            load_dotenv(prof_env_file, override=True)

        return Settings()
    except ValidationError as e:
        raise e


if __name__ == "__main__":
    settings = load_settings()
    print("=== Settings Loaded ===")
    print("App Name:", settings.app_name)
    print("Profile:", settings.profile)
    print("CORS Allow Origins:", settings.cors_allow_origins_list)
    print("JWT Algorithm:", settings.jwt_algorithm)
    print("Docs URL:", settings.docs_url)
    print("ReDoc URL:", settings.redoc_url)
    print("OpenAPI URL:", settings.openapi_url)
    print("GMS API Key:", settings.gms_api_key)
    print("GMS API URL:", settings.gms_api_url)
    print("MySQL URL:", settings.mysql_url)
    print("MySQL Username:", settings.mysql_username)
    print("Redis Host:", settings.redis_host)
    print("Redis Port:", settings.redis_port)
    print("S3 Bucket:", settings.s3_bucket)
    print("OpenVidu URL:", settings.openvidu_url)
    print("OpenVidu Secret:", settings.openvidu_secret)
    print("OpenVidu Session Prefix:", settings.openvidu_session_prefix)
    print("=== Settings Loaded ===")
