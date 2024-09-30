import io
from typing import cast

import requests

from app.domain import ports


class OpenAITranscriptionClient(ports.TranscriptionPort):
    def __init__(
        self,
        api_key: str,
        api_url: str,
        transcription_model: str,
    ):
        self._api_key = api_key
        self._api_url = api_url
        self._model = transcription_model
        self._client = requests.Session()

    def transcribe_audio(self, audio_file: bytes) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        files = {"file": ("audio.m4a", io.BytesIO(audio_file), "audio/m4a")}
        data = {"model": self._model}
        response = self._client.post(
            url=self._api_url, headers=headers, files=files, data=data
        )
        response.raise_for_status()
        return cast(str, response.json()["text"])
