import abc
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import ai

from app.domain import models


class ChatRepository(abc.ABC):
    @abc.abstractmethod
    def save_chat(self, chat: models.Chat) -> None:
        pass

    @abc.abstractmethod
    def get_chat(self, chat_id: str) -> models.Chat | None:
        pass


class AgentPort(abc.ABC):
    @abc.abstractmethod
    def __call__(self, query: str) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def get_conversation_history(self) -> list[ai.BaseMessage]:
        ...

    @abc.abstractmethod
    def set_memory_variables(self, history: list[ai.BaseMessage]) -> None:
        ...

    @abc.abstractmethod
    def get_last_response(self) -> str:
        ...


class TranscriptionPort(ABC):
    @abstractmethod
    def transcribe_audio(self, audio_file: bytes) -> str:
        pass
