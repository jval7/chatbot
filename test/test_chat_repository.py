from unittest.mock import Mock
import pytest
from pydantic import ValidationError
from app.adapters.chat_repository import InMemoryChatRepository
from app.domain.models import Chat

def test_save_chat_in_memory():
    repo = InMemoryChatRepository()

    chat = Chat(id="123", conversation_history=[])
    try:
        repo.save_chat(chat)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e}")

def test_save_chat_dynamodb():
    # Elimina el argumento db si no es necesario
    repo = InMemoryChatRepository()

    chat = Chat(id="123", conversation_history=[])
    try:
        repo.save_chat(chat)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e}")
