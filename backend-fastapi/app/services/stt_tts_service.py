from abc import ABC, abstractmethod
from typing import Optional


class SttTtsService(ABC):
    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        pass

    @abstractmethod
    async def text_to_text(self, text: str) -> str:
        pass

    @abstractmethod
    async def text_to_speech(self, text: str) -> bytes:
        pass

    @abstractmethod
    def handle_worker_response(self, player_choice: str):
        pass
