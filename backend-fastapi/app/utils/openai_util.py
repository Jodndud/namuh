import base64
import io
from typing import Union
from openai import OpenAI


class OpenAIUtil:
    def __init__(self, api_url: str, api_key: str):
        self.client = OpenAI(base_url=api_url, api_key=api_key)

    async def stt(
        self, audio_data: Union[bytes, io.BytesIO], model: str = "whisper-1"
    ) -> str:
        if isinstance(audio_data, bytes):
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"
        else:
            audio_file = audio_data

        response = self.client.audio.transcriptions.create(file=audio_file, model=model)
        return response.text

    def tts(
        self, text: str, model: str = "gpt-4o-mini-tts", voice: str = "sage"
    ) -> bytes:
        response = self.client.audio.speech.create(model=model, voice=voice, input=text)

        return response.content
