import pytest
from app.domain import ports, models
from app.services.usecases import ChatService, NoChatFound
from unittest.mock import MagicMock, patch


# Fixtures
@pytest.fixture
def mock_agent():
    return MagicMock(spec=ports.AgentPort)


@pytest.fixture
def mock_db():
    return MagicMock(spec=ports.ChatRepository)


@pytest.fixture
def mock_transcriber():
    return MagicMock(spec=ports.TranscriptionPort)


@pytest.fixture
def fake_chat_service(mock_agent, mock_db, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


@pytest.fixture
def mock_chat():
    return MagicMock(spec=models.Chat)


# Función para obtener los datos esperados de cada test
def get_expected_data():
    return {
        "conversation_id": "mock_conversation_id",
        "query": "mock_query",
        "voice_file": b"mock_voice_file"
    }


# Funcion para reducir la duplicacion en las funciones 'continue_conversation' tests
def setup_continue_conversation_mocks(mock_db, mock_agent, mock_transcriber, expected_data, chat):
    mock_db.get_chat.return_value = chat
    mock_transcriber.transcribe_audio.return_value = expected_data["query"]
    mock_agent.get_conversation_history.return_value = []
    mock_agent.get_last_response.return_value = "mock_response"


# Tests
def test_should_start_chat_when_calling_start_chat(fake_chat_service, mock_db):
    # Arrange
    expected_data = get_expected_data()
    mock_chat_model = MagicMock(spec=models.Chat)
    mock_chat_model.id = expected_data["conversation_id"]  #
    mock_db.save_chat.return_value = None
    # Act
    with patch('app.domain.models.Chat', return_value=mock_chat_model):
        response = fake_chat_service.start_conversation()
    # Assert
    mock_db.save_chat.assert_called_once()
    assert response == expected_data["conversation_id"]


def test_should_continue_conversation_when_calling_continue_conversation(fake_chat_service, mock_agent, mock_db,mock_transcriber):
    # Arrange
    expected_data = get_expected_data()
    chat = models.Chat(id=expected_data["conversation_id"])
    mock_db.save_chat.return_value = expected_data["conversation_id"]
    setup_continue_conversation_mocks(mock_db, mock_agent, mock_transcriber, expected_data, chat)
    # Act
    response = fake_chat_service.continue_conversation(expected_data["conversation_id"], expected_data["query"], expected_data["voice_file"])
    # Assert
    mock_db.get_chat.assert_called_once_with(expected_data["conversation_id"])
    assert response == "mock_response"


def test_should_continue_conversation_when_no_chat_found(fake_chat_service, mock_db):
    # Arrange
    expected_data = get_expected_data()
    mock_db.get_chat.return_value = None
    # Act
    with pytest.raises(NoChatFound) as exc_info:
        fake_chat_service.continue_conversation(expected_data["conversation_id"], expected_data["query"],expected_data["voice_file"])
    # Assert
    mock_db.get_chat.assert_called_once_with(expected_data["conversation_id"])
    assert str(exc_info.value) == "Chat not found"


def test_should_update_chat_when_calling_update_chat(fake_chat_service, mock_agent, mock_db, mock_transcriber,mock_chat):
    # Arrange
    expected_data = get_expected_data()
    mock_chat.id = expected_data["conversation_id"]
    setup_continue_conversation_mocks(mock_db, mock_agent, mock_transcriber, expected_data, mock_chat)
    # Como el usecase hace una instancia del Chat model, debemos hacer un patch para que el Chat instanceado sea el mismo mock_chat
    with patch("app.services.usecases.models.Chat") as mock_new_chat:
        mock_new_chat.return_value = mock_chat  # Hacemos que el Chat instanceado sea el mismo mock_chat
        # Act
        response = fake_chat_service.continue_conversation(expected_data["conversation_id"], expected_data["query"],expected_data["voice_file"])
        # Assert
        mock_db.get_chat.assert_called_once_with(expected_data["conversation_id"])
        mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())
        mock_chat.update_conversation.assert_called_once_with(mock_agent.get_conversation_history())
        mock_db.save_chat.assert_called_once_with(mock_chat)
        assert response == "mock_response"
