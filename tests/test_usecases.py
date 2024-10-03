from unittest.mock import Mock, MagicMock, patch

import pytest

from app.domain import ports, models
from app.services import usecases
from app.adapters import chat_repository
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

def test_should_start_conversation_when_start_conversation_is_called(chat_service, mock_db):
        # Arrange
        with patch('app.domain.models.Chat', return_value=MagicMock(id="123")) as mock_chat:

                #Act
                result = chat_service.start_conversation()

                #Assert
                mock_db.save_chat.assert_called_once_with(mock_chat.return_value)
                assert result == "123"

def test_should_continue_conversation_when_continue_conversation_is_called(chat_service, mock_db, mock_agent):
        # Arrange
        with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:

                conversation_id = "123"
                query = "Hello"
                mock_chat.return_value.get_conversation_history.return_value = []
                mock_db.get_chat.return_value = mock_chat.return_value
                mock_agent.get_last_response.return_value = "Hi"

                # Act
                result = chat_service.continue_conversation(conversation_id, query)

                # Assert
                mock_db.get_chat.assert_called_once_with(conversation_id)
                mock_agent.set_memory_variables.assert_called_once_with([])
                mock_agent.get_last_response.assert_called_once()
                mock_agent.get_conversation_history.assert_called_once()
                mock_db.save_chat.assert_called_once()

                assert result == "Hi"

def test_should_raise_exception_when_continue_conversation_is_called_with_invalid_conversation_id(chat_service, mock_db):
        # Arrange
        conversation_id = "321"
        query = "Hello"
        mock_db.get_chat.return_value = None

        # Act
        with pytest.raises(NoChatFound) as exc:
                chat_service.continue_conversation(conversation_id, query=query)


        # Assert
        assert str(exc.value) == "Chat not found"

def test_should_raise_exception_when_continue_conversation_is_called_with_no_input(chat_service, mock_db):
        # Arrange
        conversation_id = "123"
        query = None

        # Act & Assert
        with pytest.raises(InputNotProvided) as exc:
                chat_service.continue_conversation(conversation_id, query=query)

        # Assert
        assert str(exc.value) == "No input provided"

def test_should_continue_conversation_when_continue_conversation_is_called_with_voice_file(chat_service, mock_db, mock_agent, mock_transcriber):
        # Arrange
        with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:

                conversation_id = "123"
                voice_file = b"audio"

                mock_chat.return_value.get_conversation_history.return_value = []
                mock_db.get_chat.return_value = mock_chat.return_value
                mock_agent.get_last_response.return_value = "Hi"
                mock_transcriber.transcribe_audio.return_value = "Hello"

                # Act
                result = chat_service.continue_conversation(conversation_id, voice_file=voice_file)

                # Assert
                mock_db.get_chat.assert_called_once_with(conversation_id)
                mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
                mock_agent.set_memory_variables.assert_called_once_with([])
                mock_agent.get_last_response.assert_called_once()
                mock_agent.get_conversation_history.assert_called_once()
                mock_db.save_chat.assert_called_once_with(mock_chat.return_value)