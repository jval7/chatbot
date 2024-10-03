import pytest
from unittest.mock import Mock, patch
from typing import List

from app.services import usecases
from app.domain import ports, models
from app.services.usecases import ChatService, InputNotProvided, NoChatFound


class TestChatService:
    @pytest.fixture
    def mock_agent(self):
        return Mock(spec=ports.AgentPort)

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=ports.ChatRepository)

    @pytest.fixture
    def mock_transcriber(self):
        return Mock(spec=ports.TranscriptionPort)

    @pytest.fixture
    def chat_service(self, mock_agent, mock_db, mock_transcriber):
        return ChatService(
            agent=mock_agent,
            db=mock_db,
            transcriber=mock_transcriber
        )

    def test_start_conversation(self, chat_service, mock_db):
        # Arrange
        mock_db.save_chat.return_value = None

        # Act
        result = chat_service.start_conversation()

        # Assert
        assert result is not None
        mock_db.save_chat.assert_called_once()

    def test_update_chat(self, chat_service, mock_agent, mock_db):
        # Arrange
        mock_agent.get_conversation_history.return_value = []
        test_chat = models.Chat(id="1112148222")

        # Act
        chat_service._update_chat(test_chat)

        # Assert
        mock_db.save_chat.assert_called_once()
        saved_chat = mock_db.save_chat.call_args[0][0]
        assert saved_chat.id == "1112148222"
        assert saved_chat.get_conversation_history() == []

    def test_continue_conversation_with_voice(
        self, chat_service, mock_agent, mock_transcriber, mock_db
    ):
        # Arrange
        mock_db.get_chat.return_value = models.Chat(id="1248765")
        mock_agent.get_last_response.return_value = "response"
        mock_transcriber.transcribe_audio.return_value = "query"
        test_voice_file = b"voice file"

        # Act
        result = chat_service.continue_conversation("1248765", voice_file=test_voice_file)

        # Assert
        assert result == "response"
        mock_transcriber.transcribe_audio.assert_called_once_with(test_voice_file)
        mock_db.get_chat.assert_called_once_with("1248765")
        mock_agent.set_memory_variables.assert_called_once()
        mock_agent.assert_called_once_with(query="query")
        mock_db.save_chat.assert_called_once()

    def test_continue_conversation_without_input(self, chat_service):
        # Act & Assert
        with pytest.raises(InputNotProvided):
            chat_service.continue_conversation(conversation_id="1112148222")

    def test_continue_conversation_chat_not_found(self, chat_service, mock_db):
        # Arrange
        mock_db.get_chat.return_value = None

        # Act & Assert
        with pytest.raises(NoChatFound):
            chat_service.continue_conversation(conversation_id="1112148222", query="query")
