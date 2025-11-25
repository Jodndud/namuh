from fastapi import APIRouter

from .health_controller import health_controller
from .stt_tts_controller import stt_tts_controller
from .s3_controller import s3_controller
from .mqtt_controller import mqtt_controller


class ControllerConfig:
    @staticmethod
    def get_all_routers():
        return [
            health_controller(),
            stt_tts_controller(),
            s3_controller(),
            mqtt_controller(),
        ]
