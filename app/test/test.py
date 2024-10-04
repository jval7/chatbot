from unittest.mock import Mock, MagicMock, patch
import pytest
from app.domain import ports
from app.services import usecases
from app.services.usecases import NoChatFound, InputNotProvided


@pytest.fixture
def mock_agent():
    return Mock(spec=ports.AgentPort)


@pytest.fixture
def mock_db():
    return Mock(spec=ports.ChatRepository)


@pytest.fixture
def mock_transcriber():
    return Mock(spec=ports.TranscriptionPort)


@pytest.fixture
def chat_service(mock_agent, mock_db, mock_transcriber):
    return usecases.ChatService(mock_agent, mock_db, mock_transcriber)


def test_continue_conversation_with_voice_file(chat_service, mock_db, mock_agent, mock_transcriber):
    with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:
        conversation_id = "456"
        voice_file = b"audio_data"

        mock_chat.return_value.get_conversation_history.return_value = []
        mock_db.get_chat.return_value = mock_chat.return_value
        mock_agent.get_last_response.return_value = "Hey there"
        mock_transcriber.transcribe_audio.return_value = "Hi there"

        result = chat_service.continue_conversation(conversation_id, voice_file=voice_file)

        mock_db.get_chat.assert_called_once_with(conversation_id)
        mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
        mock_agent.set_memory_variables.assert_called_once_with([])
        mock_agent.get_last_response.assert_called_once()
        mock_agent.get_conversation_history.assert_called_once()
        mock_db.save_chat.assert_called_once_with(mock_chat.return_value)

        assert result == "Hey there"


def test_continue_conversation_invalid_conversation_id(chat_service, mock_db):
    conversation_id = "999"
    query = "Hello World"
    mock_db.get_chat.return_value = None

    with pytest.raises(NoChatFound) as exc:
        chat_service.continue_conversation(conversation_id, query=query)

    assert str(exc.value) == "Chat not found"


def test_continue_conversation_no_input(chat_service, mock_db):
    conversation_id = "456"
    query = None

    with pytest.raises(InputNotProvided) as exc:
        chat_service.continue_conversation(conversation_id, query=query)

    assert str(exc.value) == "No input provided"


def test_start_conversation(chat_service, mock_db):
    with patch('app.domain.models.Chat', return_value=MagicMock(id="789")) as mock_chat:
        result = chat_service.start_conversation()

        mock_db.save_chat.assert_called_once_with(mock_chat.return_value)
        assert result == "789"


def test_continue_conversation(chat_service, mock_db, mock_agent):
    with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:
        conversation_id = "456"
        query = "Hi there"
        mock_chat.return_value.get_conversation_history.return_value = []
        mock_db.get_chat.return_value = mock_chat.return_value
        mock_agent.get_last_response.return_value = "Hello back"

        result = chat_service.continue_conversation(conversation_id, query)

        mock_db.get_chat.assert_called_once_with(conversation_id)
        mock_agent.set_memory_variables.assert_called_once_with([])
        mock_agent.get_last_response.assert_called_once()
        mock_agent.get_conversation_history.assert_called_once()
        mock_db.save_chat.assert_called_once()

        assert result == "Hello back"
