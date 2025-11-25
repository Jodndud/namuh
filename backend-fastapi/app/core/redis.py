import redis
import json
from app.core.load_settings import Settings


class Redis:
    def __init__(self, settings: Settings) -> None:
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )

    def get_client(self) -> redis.Redis:
        return self.client

    def ping(self) -> bool:
        return self.client.ping()
    
    def rpush(self, key: str, value: str):
        return self.client.rpush(key, value)

    # 조회
    def lrange(self, key: str, start: int, end: int):
        return self.client.lrange(key, start, end)