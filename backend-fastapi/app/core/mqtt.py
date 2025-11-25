import asyncio
import json
import logging
import ssl
import base64
from typing import Callable, Dict, Optional
from aiomqtt import Client, MqttError
from app.core.load_settings import Settings
from app.services.implementation.tts_input_service_impl import TTSInputServiceImpl
from app.utils.openai_util import OpenAIUtil
from app.core.redis import Redis


class MQTTClient:
    def __init__(self, settings: Settings, logger: logging.Logger, redis: Redis):
        self.settings = settings
        self.logger = logger
        self.redis = redis
        self.client: Optional[Client] = None
        self.subscriptions: Dict[str, Callable[[str], None]] = {}
        self._running = False
        self._client_task: Optional[asyncio.Task] = None
        self.openai_util = OpenAIUtil(
            api_url=getattr(settings, "gms_api_url", None),
            api_key=getattr(settings, "gms_api_key", None),
        )
        self.topic_key = settings.redis_topic_key

    async def start(self):
        self._client_task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._client_task:
            self._client_task.cancel()
            try:
                await self._client_task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        while True:
            try:
                tls_context = ssl.create_default_context()

                async with Client(
                    hostname=self.settings.mqtt_host,
                    port=self.settings.mqtt_port,
                    username=self.settings.mqtt_username,
                    password=self.settings.mqtt_password,
                    keepalive=self.settings.mqtt_keepalive,
                    tls_context=tls_context,
                ) as client:
                    self.client = client
                    self._running = True
                    self.logger.info("Connected to MQTT broker")

                    # 시작할 때 구독
                    async def _subscribe_on_connect():
                        # wait until the client is connected
                        while not (self._running and self.client):
                            await asyncio.sleep(0.1)

                        # Redis에서 조회 후 구독
                        key = self.topic_key
                        try:
                            topics = self.redis.lrange(key, 0, -1)

                            if not topics:
                                self.logger.info(f"No topics found in Redis key: {key}")
                                return

                            for topic in topics:
                                await self.client.subscribe(topic)
                                self.logger.info(
                                    f"subscribed to topic from Redis: {topic}"
                                )

                        except Exception as e:
                            self.logger.error(
                                f"Failed to auto-subscribe topics from Redis: {e}"
                            )

                    asyncio.create_task(_subscribe_on_connect())

                    async for message in client.messages:
                        topic = str(message.topic)
                        payload = message.payload.decode()

                        self.logger.info(f"메시지 수신: {topic} -> {payload}")

                        if topic in self.subscriptions:
                            await self.subscriptions[topic](topic, payload)

                        if topic == "buriburi/robot/all/command":
                            # TTS변환
                            tts_service = TTSInputServiceImpl()
                            command = (
                                payload.replace("\n", "")
                                .replace(" ", "")
                                .split('"command":"')[1]
                                .split('"')[0]
                            )

                            # init_pose이니면 tts
                            if command != "init_pose":
                                tts_text = tts_service.get_tts_input(command)
                                audio_bytes = self.openai_util.tts(tts_text)
                                encoded_audio = base64.b64encode(audio_bytes).decode(
                                    "utf-8"
                                )

                                await self.publish(
                                    topic="buriburi/robot/all/tts",
                                    payload=encoded_audio,
                                )

            except MqttError as e:
                self.logger.error(f"MQTT 연결 오류: {e}")
                self.client = None
                self._running = False

                await asyncio.sleep(5)
                self.logger.info("MQTT 재연결 시도...")

            except asyncio.CancelledError:
                self.logger.info("MQTT 클라이언트 중지")
                self.client = None
                self._running = False
                break
            except Exception as e:
                self.logger.error(f"예상치 못한 오류: {e}")
                await asyncio.sleep(5)

    async def publish(self, payload: str, topic: str = "buriburi/robot/all/command"):
        if not self.client or not self._running:
            self.logger.error("MQTT 클라이언트가 연결되지 않았습니다.")
            raise MqttError("MQTT client not connected")

        try:
            await self.client.publish(topic, payload)
            self.logger.info(f"메시지 발행: {topic}")
        except MqttError as e:
            self.logger.error(f"메시지 발행 실패: {e}")
            raise

    async def subscribe(self, topic: str, callback: Callable):
        if not self.client or not self._running:
            self.logger.error("MQTT 클라이언트가 연결되지 않았습니다.")
            raise MqttError("MQTT client not connected")

        try:
            await self.client.subscribe(topic)
            self.subscriptions[topic] = callback
            self.logger.info(f"토픽 구독: {topic}")
        except MqttError as e:
            self.logger.error(f"토픽 구독 실패: {e}")
            raise

    async def unsubscribe(self, topic: str):
        if not self.client or not self._running:
            self.logger.error("MQTT 클라이언트가 연결되지 않았습니다.")
            return

        try:
            await self.client.unsubscribe(topic)
            self.subscriptions.pop(topic, None)
            self.logger.info(f"토픽 구독 해제: {topic}")
        except MqttError as e:
            self.logger.error(f"토픽 구독 해제 실패: {e}")
            raise

    def is_connected(self) -> bool:
        return self._running and self.client is not None

    def _send_audio(self, audio_data: bytes):
        if not self.client or not self._running:
            self.logger.error("MQTT 클라이언트가 연결되지 않았습니다.")
            return

        encoded_audio = base64.b64encode(audio_data).decode("utf-8")

        asyncio.create_task(
            self.publish(topic="buriburi/robot/all/tts", payload=encoded_audio)
        )
