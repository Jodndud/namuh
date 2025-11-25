import asyncio
import base64
import json
from random import random
import re
from ..stt_tts_service import SttTtsService
from ...utils.openai_util import OpenAIUtil
from ...utils.rsp_util import ExerciseGameHandler
from ...schemas.tts_enum import match_stt_to_tts_response
from typing import Optional


class SttTtsServiceImpl(SttTtsService):
    def __init__(self, settings, logger, mqtt_client):
        self.settings = settings
        self.logger = logger
        self.openai_util = OpenAIUtil(
            api_url=getattr(settings, "gms_api_url", None),
            api_key=getattr(settings, "gms_api_key", None),
        )
        self.mqtt_client = mqtt_client
        self.exercise_handler = ExerciseGameHandler(mqtt_client, logger)

        self.mqtt_client.subscriptions["rsp_res"] = self._handle_rsp_response

    async def _handle_rsp_response(self, topic: str, payload: str):
        self.logger.info(f"Received RSP response on {topic}: {payload}")
        self.handle_worker_response(payload)

    async def _process_text(self, text: str) -> None:
        if "체조" in text:
            self.logger.info("Detected command to start exercise")
            await self.exercise_handler.start_excercise_game(self.text_to_speech)
            return

        tts_response, command = match_stt_to_tts_response(text)

        if tts_response:
            self.logger.info(
                f"Matched text to TTS response: {tts_response} for command: {command}"
            )
            await self.text_to_speech(tts_response)

            if command:
                await self._publish_command(command)
        else:
            self.logger.info("No matching TTS response found for input text")
            await self.text_to_speech(text)

    async def _publish_command(self, command: str) -> None:
        try:
            command_payload = json.dumps(
                {
                    "type": "command",
                    "command": command,
                    "who": "backend",
                    "robot_id": "all",
                }
            )
            await self.mqtt_client.publish(
                payload=command_payload, topic="buriburi/robot/all/command"
            )
            self.logger.info(f"Published command {command} to MQTT")
        except Exception as e:
            self.logger.error(f"Failed to publish command {command} to MQTT: {e}")
        finally:
            await asyncio.sleep(1)
            await self.mqtt_client.publish(
                payload=json.dumps(
                    {
                        "type": "command",
                        "command": "init_pose",
                        "who": "backend",
                        "robot_id": "all",
                    }
                ),
                topic="buriburi/robot/all/command",
            )

    async def text_to_text(self, text: str) -> str:
        self.logger.info("Text-to-Text requested")

        if "체조" in text:
            self.logger.info("Detected command to start exercise")
            await self.exercise_handler.start_excercise_game(self.text_to_speech)
            return text
        tts_response, command = match_stt_to_tts_response(text)

        if tts_response:
            self.logger.info(
                f"Matched text to TTS response: {tts_response} for command: {command}"
            )
            await self.text_to_speech(tts_response)

            if command:
                command_payload = json.dumps(
                    {
                        "type": "command",
                        "command": command,
                        "who": "backend",
                        "robot_id": "all",
                    }
                )
                await self.mqtt_client.publish(
                    payload=command_payload, topic="buriburi/robot/all/command"
                )
                self.logger.info(f"Published command {command} to MQTT")
        else:
            self.logger.info("No matching TTS response found for input text")
            await self.text_to_speech(text)

        return text

    def check_kor(self, text: str) -> bool:
        p = re.compile("[가-힣]")
        r = p.search(text)
        return bool(r)

    async def speech_to_text(
        self, audio_data: bytes, filename: str = "audio.webm"
    ) -> str:
        self.logger.info("Speech-to-Text requested")
        result = await self.openai_util.stt(audio_data)

        if not self.check_kor(result):
            self.logger.info("STT result does not contain Korean characters")
            await self.text_to_speech("다시 한 번 말해줄래?")
            return result

        exercise_keywords = ("체조", "세수", "제조", "세조")

        if any(keyword in result for keyword in exercise_keywords):
            self.logger.info("Detected command to start exercise")
            await self.exercise_handler.start_excercise_game(self.text_to_speech)
            return result

        tts_response, command = match_stt_to_tts_response(result)
        if tts_response:
            self.logger.info(
                f"Matched STT result to TTS response: {tts_response} for command: {command}"
            )
            await self.text_to_speech(tts_response)

            if command:
                command_payload = json.dumps(
                    {
                        "type": "command",
                        "command": command,
                        "who": "backend",
                        "robot_id": "all",
                    }
                )
                await self.mqtt_client.publish(
                    payload=command_payload, topic="buriburi/robot/all/command"
                )
                self.logger.info(f"Published command {command} to MQTT")
        else:
            self.logger.info("No matching TTS response found for STT result")
            await self.text_to_speech(result)

        return result

    async def text_to_speech(self, text: str) -> bytes:
        self.logger.info("Text-to-Speech requested")
        try:
            audio_data = await asyncio.to_thread(self.openai_util.tts, text)

            payload = {
                "audio_base64": base64.b64encode(audio_data).decode("utf-8"),
                "mime_type": "audio/mpeg",
            }
            payload = json.dumps(payload)

            await self.mqtt_client.publish(
                payload=payload, topic="buriburi/robot/all/tts"
            )
            return audio_data
        except Exception as e:
            self.logger.error(f"Text-to-Speech failed: {e}")
            raise

    def handle_worker_response(self, payload):
        self.exercise_handler.handle_worker_response(payload)
