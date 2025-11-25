from pydantic import BaseModel
from app.schemas.mqtt_enum import MQTTCommand
from app.schemas.tts_enum import TTSInputMapping
from typing import Optional


class MQTTPayload(BaseModel):
    type: str = "status"
    command: Optional[MQTTCommand | TTSInputMapping | str]
    who: str = "backend"
    robot_id: str = "all"

    class Config:
        json_schema_extra = {
            "example": {
                "type": "command",
                "command": "init_pose",
                "who": "backend",
                "robot_id": "all",
            }
        }


class MQTTPublishRequest(BaseModel):
    topic: str
    payload: MQTTPayload

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "buriburi/robot/all/command",
                "payload": {
                    "type": "command",
                    "command": "init_pose",
                    "who": "backend",
                    "robot_id": "all",
                },
            }
        }


class MQTTSubscribeRequest(BaseModel):
    topic: str
