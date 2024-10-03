from unittest.mock import Mock, MagicMock
from app.services import usecases
from app.domain import ports, models
import pytest

###### PARCIAL #2 - PRUEBAS UNITARIAS ######

@pytest.fixture
def mock_agent():
    agent = Mock(spec=ports.AgentPort)
    return agent

@pytest.fixture
def mock_db():
    db = Mock(spec=ports.ChatRepository)
    return db

@pytest.fixture
def mock_transcriber():
    transcriber = Mock(spec=ports.TranscriptionPort)
    return transcriber

@pytest.fixture
def test_chat_service(mock_agent, mock_db, mock_transcriber):
    return usecases.ChatService(mock_agent, mock_db, mock_transcriber)


def test_should_start_conversation_when_calling_chat_service_start_conversation_method(test_chat_service, mock_db):
    # Arrange
    mock_chat = MagicMock()
    mock_chat.id = "123"
    models.Chat = MagicMock(return_value=mock_chat)

    # Act
    chat_id = test_chat_service.start_conversation()
    mock_db.save_chat.assert_called_once_with(mock_chat)

    # Assert
    assert chat_id == mock_chat.id


def test_should_continue_conversation_when_calling_chat_service_continue_conversation_method(test_chat_service, mock_db, mock_agent):
    # Arrange
    conversation_id = "123"
    query = "¿Cual es mi color favorito?"

    chat_model = MagicMock()
    chat_model.id = conversation_id
    chat_model.get_conversation_history.return_value = []

    mock_db.get_chat.return_value = chat_model
    mock_agent.get_last_response.return_value = "El negro!"

    # Act
    response = test_chat_service.continue_conversation(conversation_id, query=query)

    # Assert
    mock_db.get_chat.assert_called_once_with(conversation_id)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    assert response == "El negro!"

def test_should_raise_exception_when_calling_chat_service_continue_conversation_method_without_input(test_chat_service):
    # Arrange
    conversation_id = "123"

    # Act & Assert
    with pytest.raises(usecases.InputNotProvided, match="No input provided"):
        test_chat_service.continue_conversation(conversation_id)

def test_should_raise_exception_when_calling_chat_service_update_chat_method_without_chat(test_chat_service):
    # Arrange
    chat = None

    # Act & Assert
    with pytest.raises(usecases.NoChatFound, match="Chat not found"):
        test_chat_service._update_chat(chat)


def test_should_update_chat_when_calling_chat_service_update_chat_method(test_chat_service, mock_db, mock_agent):
    # Arrange
    mock_chat = MagicMock()
    mock_chat.id = "123"
    mock_conversation_history = ["Hola", "Adios"]

    # Act
    mock_agent.get_conversation_history = MagicMock(return_value=mock_conversation_history)
    models.Chat = MagicMock()
    test_chat_service._update_chat(mock_chat)

    # Assert
    models.Chat.assert_called_once_with(id=mock_chat.id)
    new_chat = models.Chat.return_value
    new_chat.update_conversation.assert_called_once_with(
        mock_conversation_history)
    mock_db.save_chat.assert_called_once_with(new_chat)
