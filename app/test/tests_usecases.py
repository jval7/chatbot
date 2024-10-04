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

def test_should_start_conversation_when_start_conversation_is_called(chat_service, mock_db):
        # Arrange
        new_chat_id = "111"
        with patch('app.domain.models.Chat', return_value=MagicMock(id=new_chat_id)) as mock_chat:

                # Act
                result = chat_service.start_conversation()

                # Assert
                mock_db.save_chat.assert_called_once_with(mock_chat.return_value)
                assert result == new_chat_id

def test_should_continue_conversation_when_continue_conversation_is_called(chat_service, mock_db, mock_agent):
        # Arrange
        new_response = "¿Si funciono?"  # Cambiado de expected_response a new_response
        with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:

                new_conversation_id = "981"
                query = "¿Si funcionas?"
                mock_chat.return_value.get_conversation_history.return_value = []
                mock_db.get_chat.return_value = mock_chat.return_value
                mock_agent.get_last_response.return_value = new_response

                # Act
                result = chat_service.continue_conversation(new_conversation_id, query)

                # Assert
                mock_db.get_chat.assert_called_once_with(new_conversation_id)
                mock_agent.set_memory_variables.assert_called_once_with([])
                mock_agent.get_last_response.assert_called_once()
                mock_agent.get_conversation_history.assert_called_once()
                mock_db.save_chat.assert_called_once()

                assert result == new_response

def test_should_raise_exception_when_continue_conversation_is_called_with_invalid_conversation_id(chat_service, mock_db):
        # Arrange
        invalid_conversation_id = "092"
        query = "¿Como estas?"
        expected_error_message = "Chat not found"
        mock_db.get_chat.return_value = None

        # Act
        with pytest.raises(NoChatFound) as exc:
                chat_service.continue_conversation(invalid_conversation_id, query=query)

        # Assert
        assert str(exc.value) == expected_error_message

def test_should_raise_exception_when_continue_conversation_is_called_with_no_input(chat_service, mock_db):
        # Arrange
        new_conversation_id = "910"  # Cambiado de conversation_id a new_conversation_id
        query = None
        expected_error_message = "No input provided"

        # Act & Assert
        with pytest.raises(InputNotProvided) as exc:
                chat_service.continue_conversation(new_conversation_id, query=query)

        # Assert
        assert str(exc.value) == expected_error_message

def test_should_continue_conversation_when_continue_conversation_is_called_with_voice_file(chat_service, mock_db, mock_agent, mock_transcriber):
        # Arrange
        new_response = "¿Me estas testeando?"
        new_transcription = "Sisas"
        with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:

                new_conversation_id = "456"
                voice_file = b"audio"

                mock_chat.return_value.get_conversation_history.return_value = []
                mock_db.get_chat.return_value = mock_chat.return_value
                mock_agent.get_last_response.return_value = new_response
                mock_transcriber.transcribe_audio.return_value = new_transcription

                # Act
                result = chat_service.continue_conversation(new_conversation_id, voice_file=voice_file)

                # Assert
                mock_db.get_chat.assert_called_once_with(new_conversation_id)
                mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
                mock_agent.set_memory_variables.assert_called_once_with([])
                mock_agent.get_last_response.assert_called_once()
                mock_agent.get_conversation_history.assert_called_once()
                mock_db.save_chat.assert_called_once_with(mock_chat.return_value)

                assert result == new_response