from pydantic import BaseModel, Field
from typing import Optional


class STTRequestDTO(BaseModel):
    audio_base64: str = Field(..., description="오디오 파일의 Base64 인코딩 문자열")
    filename: Optional[str] = Field(None, description="오디오 파일의 이름 (선택 사항)")
    mime_type: Optional[str] = Field(
        "audio/mpeg", description="오디오 파일의 MIME 타입 (선택 사항)"
    )


class STTResponseDTO(BaseModel):
    text: str = Field(..., description="변환된 텍스트")


class TTSRequestDTO(BaseModel):
    text: str = Field(..., description="음성으로 변환할 텍스트")
