from fastapi import APIRouter, Depends, UploadFile, File, Body
from dependency_injector.wiring import Provide, inject

import base64

from app.core.containers import Container
from ..services.stt_tts_service import SttTtsService

from app.schemas.stt_dto import STTRequestDTO, STTResponseDTO, TTSRequestDTO


from app.core.exceptions.custom_exception import STTServiceException


@inject
def stt_tts_controller(
    stt_tts_service: SttTtsService = Depends(Provide[Container.stt_tts_service]),
) -> APIRouter:
    router = APIRouter(prefix="/stt-tts", tags=["STT & TTS"])

    @router.post(
        "/speech-to-text",
        summary="Speech to Text (JSON Base64)",
        description="Base64로 전달된 오디오를 텍스트로 변환합니다.",
        response_model=STTResponseDTO,
        include_in_schema=False,
    )
    async def speech_to_text_endpoint(dto: STTRequestDTO = Body(...)):
        try:
            audio_bytes = base64.b64decode(dto.audio_base64)
            text = await stt_tts_service.speech_to_text(audio_bytes)
            return STTResponseDTO(text=text)
        except:
            raise STTServiceException()

    @router.post(
        "/text-to-text",
        summary="Text to Text",
        description="텍스트를 받아 동일한 텍스트를 반환합니다.",
    )
    async def text_to_text_endpoint(text: str = Body(...)):
        text = await stt_tts_service.text_to_text(text)
        return {"text": text}

    @router.post(
        "/speech-to-text/file",
        summary="Speech to Text (file upload)",
        description="파일 업로드로 오디오를 전송하여 텍스트로 변환합니다.",
        response_model=STTResponseDTO,
        include_in_schema=False,
    )
    async def speech_to_text_file_endpoint(file: UploadFile = File(...)):
        try:
            audio_data = await file.read()
            text = await stt_tts_service.speech_to_text(
                audio_data, filename=file.filename
            )
            return STTResponseDTO(text=text)
        except:
            raise STTServiceException()

    @router.post(
        "/text-to-speech",
        summary="Text to Speech",
        description="텍스트를 음성(Base64)으로 변환합니다.",
        include_in_schema=False,
    )
    async def text_to_speech_endpoint(req: TTSRequestDTO = Body(...)):
        audio_bytes = await stt_tts_service.text_to_speech(req.text)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio_base64": audio_base64, "mime_type": "audio/mpeg"}

    return router
