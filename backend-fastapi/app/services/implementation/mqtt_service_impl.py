import logging
from app.core.load_settings import Settings
from ..mqtt_service import MQTTService
from ...core.mqtt import MQTTClient
from ...core.exceptions.custom_exception import *
from ...schemas.mqtt_dto import MQTTPublishRequest
from ...core.redis import Redis

class MQTTServiceImpl(MQTTService):
    def __init__(self, mqtt_client: MQTTClient, logger: logging.Logger, redis: Redis, settings:Settings):
        self.mqtt_client = mqtt_client
        self.logger = logger
        self.redis = redis
        self.topic_key = settings.redis_topic_key

    async def publish_message(self, request:MQTTPublishRequest) -> bool:
        payload_str = request.payload.model_dump_json()
        try:
            await self.mqtt_client.publish(payload_str, request.topic)
            self.logger.info(
                f"Published message to topic buriburi/robot/all/command: {request.payload}"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to publish message to topic buriburi/robot/all/command: {e}"
            )
            raise MQTTPublishException(f"Failed to publish message: {e}")
        return True

    async def subscribe_topic(self, topic: str, callback=None) -> bool:
        key = self.topic_key
        # redis에 추가
        try:
            existing_topics = self.redis.lrange(key, 0, -1)

            # 존재하면 추가 안해요
            if topic not in existing_topics:
                self.redis.rpush(key, topic)
                self.logger.info(f"Added topic to Redis list: {topic}")
            else:
                self.logger.info(f"Topic already exists in Redis list: {topic}")

        except Exception as e:
            self.logger.error(f"Failed to add topic to Redis list: {e}")
            raise DataRedisOperationException(f"Failed to save topic into Redis list: {e}")
        
        try:
            await self.mqtt_client.subscribe(topic, callback)
            self.logger.info(f"Subscribed to topic {topic}")
        except Exception as e:
            self.logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise MQTTSubscriptionException(f"Failed to subscribe to topic: {e}")
        return True

    async def unsubscribe_topic(self, topic: str) -> bool:
        try:
            await self.mqtt_client.unsubscribe(topic)
            self.logger.info(f"Unsubscribed from topic {topic}")
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from topic {topic}: {e}")
            raise MQTTUnsubscriptionException(f"Failed to unsubscribe from topic: {e}")
        return True

    async def is_connected(self) -> bool:
        return self.mqtt_client.is_connected()
