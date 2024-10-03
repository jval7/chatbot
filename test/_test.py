
from unittest.mock import Mock, MagicMock
from app.services import usecases
from app.domain import ports, models
import pytest

@pytest.fixture
def mock_chat_agent():
    agent = Mock(spec=ports.AgentPort)
    return agent

@pytest.fixture
def mock_chat_repository():
    db = Mock(spec=ports.ChatRepository)
    return db

@pytest.fixture
def mock_audio_transcriber():
    transcriber = Mock(spec=ports.TranscriptionPort)
    return transcriber

@pytest.fixture
def chat_service(mock_chat_agent, mock_chat_repository, mock_audio_transcriber):
    return usecases.ChatService(mock_chat_agent, mock_chat_repository, mock_audio_transcriber)

def test_should_initiate_conversation_when_calling_chat_service_start_conversation_method(chat_service, mock_chat_repository):
    # Arrange
    mock_conversation = MagicMock()
    mock_conversation.id = "54321"
    models.Chat = MagicMock(return_value=mock_conversation)

    # Act
    conversation_id = chat_service.start_conversation()

    # Assert
    mock_chat_repository.save_chat.assert_called_once_with(mock_conversation)
    assert conversation_id == "54321"

def test_should_continue_conversation_with_input(chat_service, mock_chat_repository, mock_chat_agent):
    # Arrange
    conversation_identifier = "test_chat_id"
    user_query = "¿Cuál es mi nombre?"

    chat_instance = MagicMock()
    chat_instance.id = conversation_identifier
    chat_instance.get_conversation_history.return_value = []

    mock_chat_repository.get_chat.return_value = chat_instance
    mock_chat_agent.get_last_response.return_value = "Juan Diego"

    # Act
    response = chat_service.continue_conversation(conversation_identifier, query=user_query)

    # Assert
    mock_chat_repository.get_chat.assert_called_once_with(conversation_identifier)
    mock_chat_agent.set_memory_variables.assert_called_once_with([])
    mock_chat_agent.assert_called_once_with(query=user_query)
    assert response == "Juan Diego"

def test_should_refresh_chat_when_calling_update_chat_method(chat_service, mock_chat_repository, mock_chat_agent):
    # Arrange
    mock_conversation = MagicMock()
    mock_conversation.id = "54321"
    mock_chat_history = ["Hola", "¿Bien o no?"]

    mock_chat_agent.get_conversation_history = MagicMock(return_value=mock_chat_history)
    models.Chat = MagicMock()

    # Act
    chat_service._update_chat(mock_conversation)

    # Assert
    models.Chat.assert_called_once_with(id=mock_conversation.id)
    updated_chat = models.Chat.return_value
    updated_chat.update_conversation.assert_called_once_with(mock_chat_history)
    mock_chat_repository.save_chat.assert_called_once_with(updated_chat)
