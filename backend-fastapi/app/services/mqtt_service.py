from abc import ABC, abstractmethod
from typing import Optional, Callable
from app.schemas.mqtt_dto import MQTTPublishRequest


class MQTTService(ABC):
    @abstractmethod
    async def publish_message(self, request: MQTTPublishRequest) -> bool:
        pass

    @abstractmethod
    async def subscribe_topic(self, topic: str, callback: Optional[Callable] = None) -> bool:
        """Subscribe to a topic. If callback is None, a default logger-only handler will be used."""
        pass

    @abstractmethod
    async def unsubscribe_topic(self, topic: str) -> bool:
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        pass
