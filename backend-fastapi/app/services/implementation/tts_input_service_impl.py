from ..tts_input_service import TTSInputService
from ...schemas.tts_enum import get_text_from_command
from typing import Optional


class TTSInputServiceImpl(TTSInputService):
    def get_tts_input(self, command: str) -> Optional[str]:
        """
        Command를 TTS 입력 텍스트로 변환
        init_pose일 때는 None 반환 (TTS 입력 없음)
        """
        if command == "init_pose":
            return None
        
        return get_text_from_command(command)
