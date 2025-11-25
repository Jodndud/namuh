import asyncio
import json
import random

from app.schemas.tts_enum import get_text_from_command


class RspUtil:
    CHOICES = ["rock", "paper", "scissors"]

    @staticmethod
    def get_random_choice() -> str:
        if not RspUtil.CHOICES:
            raise ValueError("No RPS choices available for random selection")
        return random.choice(RspUtil.CHOICES)

    @staticmethod
    def determine_winner(player_choice: str, robot_choice: str) -> str:
        player_choice = player_choice.lower()
        robot_choice = robot_choice.lower()
        if player_choice == robot_choice:
            return "Draw"
        elif (
            (player_choice == "rock" and robot_choice == "scissors")
            or (player_choice == "paper" and robot_choice == "rock")
            or (player_choice == "scissors" and robot_choice == "paper")
        ):
            return "Player Wins"
        else:
            return "Robot Wins"

    @staticmethod
    def translate_result(result: str, player_choice: str, robot_choice: str) -> str:
        """게임 결과를 한국어로 변환"""
        choice_korean = {"rock": "바위", "paper": "보", "scissors": "가위"}

        player_kr = choice_korean.get(player_choice, player_choice)
        robot_kr = choice_korean.get(robot_choice, robot_choice)

        if result == "Draw":
            return f"비겼네?"
        elif result == "Player Wins":
            return f"너가 이겼네..."
        else:
            return "내가 이겼다!"


class ExerciseGameHandler:
    def __init__(self, mqtt_client, logger):
        self.mqtt_client = mqtt_client
        self.logger = logger
        self._pending_response = None

    async def start_excercise_game(self, tts_callback):
        try:
            await tts_callback("그래")
            if not self._is_mqtt_connected():
                raise ConnectionError("MQTT client not connected")
            await self._send_prepare_status()
            await tts_callback("준비됐어? 하나 둘 셋!")
            await asyncio.sleep(5)

            robot_choice = RspUtil.get_random_choice()
            self.logger.info(f"Robot choice: {robot_choice}")

            if not self._is_mqtt_connected():
                raise ConnectionError("MQTT client not connected")

            await self._send_robot_command(robot_choice)
            await tts_callback(get_text_from_command(robot_choice))
            await self._send_worker_request()

            player_choice = await self._wait_for_worker_response(timeout=10)
            self.logger.info(f"Player choice received: {player_choice}")

            if player_choice in ["NoLandmarks", "Unknown"]:
                result = "Robot Wins"
                result_korean = "너의 포즈를 탐지하지 못했어"
            else:
                result = RspUtil.determine_winner(player_choice, robot_choice)
                self.logger.info(f"Game result: {result}")
                result_korean = RspUtil.translate_result(
                    result, player_choice, robot_choice
                )

            await tts_callback(result_korean)

            await asyncio.sleep(3)
            await self._return_to_idle()
        except asyncio.TimeoutError:
            self.logger.error("Worker response timeout")
            await tts_callback("응답 시간이 초과되었습니다")
        except Exception as e:
            self.logger.error(f"Error in exercise game: {e}")
            await tts_callback("게임 중 오류가 발생했습니다")

    async def _send_prepare_status(self):
        """체조 준비 상태 전달"""
        payload = {
            "type": "command",
            "command": "init_pose",
            "who": "backend",
            "robot_id": "all",
        }
        await self.mqtt_client.publish(
            payload=json.dumps(payload), topic="buriburi/robot/all/command"
        )

    async def _send_robot_command(self, command: str):
        """로봇에게 가위바위보 명령 전달"""
        payload = {
            "type": "command",
            "command": command,
            "who": "backend",
            "robot_id": "all",
        }
        await self.mqtt_client.publish(
            payload=json.dumps(payload), topic="buriburi/robot/all/command"
        )

    async def _send_worker_request(self):
        await self.mqtt_client.publish(payload="start", topic="rsp_req")

    async def _wait_for_worker_response(self, timeout: int = 10) -> str:
        future = asyncio.Future()
        self._pending_response = future

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        finally:
            self._pending_response = None

    def handle_worker_response(self, payload):
        try:
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
                data = json.loads(payload_str)
            elif isinstance(payload, str):
                data = json.loads(payload)
            elif isinstance(payload, dict):
                data = payload
            else:
                self.logger.error(f"Unexpected payload type: {type(payload)}")
                return

            self.logger.info(f"Handling worker response - data: {data}")

            player_choice = data.get("result")

            if player_choice is None:
                self.logger.error("No 'result' key found in worker response")
                return

            player_choice = player_choice.lower()
            self.logger.info(f"Extracted player_choice: {player_choice}")

            if self._pending_response and not self._pending_response.done():
                self._pending_response.set_result(player_choice)
                self.logger.info(f"Worker response '{player_choice}' set successfully")
            else:
                self.logger.warning(
                    f"No pending response for player_choice: {player_choice}"
                )

        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from worker: {payload}")
        except Exception as e:
            self.logger.error(f"Error in handle_worker_response: {e}")

    def _is_mqtt_connected(self) -> bool:
        try:
            return (
                hasattr(self.mqtt_client, "_running")
                and self.mqtt_client._running
                and self.mqtt_client.client is not None
            )
        except Exception:
            return False

    async def _return_to_idle(self):
        payload = {
            "type": "command",
            "command": "init_pose",
            "who": "backend",
            "robot_id": "all",
        }
        return await self.mqtt_client.publish(
            payload=json.dumps(payload), topic="buriburi/robot/all/command"
        )
