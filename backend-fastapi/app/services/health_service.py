from abc import ABC, abstractmethod


class HealthService(ABC):
    @abstractmethod
    def check_health(self) -> dict:
        pass

    @abstractmethod
    def check_health_mysql(self) -> dict:
        pass

    @abstractmethod
    def check_health_redis(self) -> dict:
        pass

    @abstractmethod
    def check_health_s3(self) -> dict:
        pass
