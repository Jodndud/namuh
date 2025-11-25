from abc import ABC, abstractmethod
from typing import Optional


class TTSInputService(ABC):
    @abstractmethod
    def get_tts_input(self, command: str) -> Optional[str]:
        pass
