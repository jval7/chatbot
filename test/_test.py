import pytest
from app.domain import ports, models
from app.services.usecases import ChatService
from unittest.mock import MagicMock


@pytest.fixture
def mock_agent():
    agent = MagicMock(spec=ports.AgentPort)
    return agent


@pytest.fixture
def mock_db():
    db = MagicMock(spec=ports.ChatRepository)
    return db


@pytest.fixture
def mock_transcriber():
    transcriber = MagicMock(spec=ports.TranscriptionPort)
    return transcriber


@pytest.fixture
def chat_service(mock_agent, mock_db, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


def test_should_start_chat_when_calling_start_chat(chat_service, mock_db):
    # Arrange
    expected_chat_model = models.Chat(id="mock_chat_id")
    mock_db.save_chat.return_value = None
    mock_db.save_chat.side_effect = lambda chat: setattr(chat, 'id', expected_chat_model.id)

    # Act
    chat_id = chat_service.start_conversation()

    # Assert
    mock_db.save_chat.assert_called_once()
    assert chat_id == expected_chat_model.id


def test_should_continue_conversation_with_query_when_calling_continue_conversation(chat_service, mock_db, mock_agent):
    # Arrange
    conversation_id = "mock_chat_id"
    query = "¿Cual es el mejor equipo de colombia?"

    chat_model = MagicMock(spec=models.Chat)
    chat_model.id = conversation_id
    chat_model.get_conversation_history.return_value = []

    mock_db.get_chat.return_value = chat_model
    mock_agent.get_last_response.return_value = "El deportivo cali!"

    # Act
    response = chat_service.continue_conversation(conversation_id, query=query)

    # Assert
    mock_db.get_chat.assert_called_once_with(conversation_id)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    assert response == "El deportivo cali!"


def test_should_update_chat_when_calling_update_chat(chat_service, mock_db, mock_agent):
    # Arrange
    chat_id = "mock_chat_id"

    chat_model = MagicMock(spec=models.Chat)
    chat_model.id = chat_id
    mock_db.get_chat.return_value = chat_model

    mock_agent.get_conversation_history.return_value = ["Hello", "How are you?"]

    # Act
    chat_service._update_chat(chat_model)

    # Assert
    mock_agent.get_conversation_history.assert_called_once()
    chat_model.update_conversation.assert_called_once_with(["Hello", "How are you?"])
    mock_db.save_chat.assert_called_once_with(chat_model)