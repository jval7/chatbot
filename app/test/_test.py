import unittest
from unittest.mock import Mock
from app.domain import models
from app.services.usecases import ChatService

class TestChatService(unittest.TestCase):
    def setUp(self):
        # Arrange
        self.agent_mock = Mock()
        self.db_mock = Mock()
        self.transcriber_mock = Mock()
        self.chat_service = ChatService(self.agent_mock, self.db_mock, self.transcriber_mock)

    def test_should_start_conversation_when_calling_new_chat(self):
        # Arrange
        chat_model_mock = Mock(spec=models.Chat)
        chat_model_mock.id = "test_id"
        models.Chat = Mock(return_value=chat_model_mock)

        # Act
        result = self.chat_service.start_conversation()

        # Assert
        self.db_mock.save_chat.assert_called_once_with(chat_model_mock)
        self.assertEqual(result, "test_id")

    def test_should_continue_conversation_when_type_a_query(self):
        # Arrange
        chat_mock = Mock()
        chat_mock.id = "test_id"
        self.db_mock.get_chat.return_value = chat_mock
        chat_mock.get_conversation_history.return_value = ["history"]
        self.agent_mock.get_last_response.return_value = "response"

        # Act
        result = self.chat_service.continue_conversation("test_id", query="Hello")

        # Assert
        self.db_mock.get_chat.assert_called_once_with("test_id")
        self.agent_mock.set_memory_variables.assert_called_once_with(["history"])
        self.agent_mock.assert_called_once_with(query="Hello")
        self.assertEqual(result, "response")

    def test_should_continue_conversation_when_upload_voice_file(self):
        # Arrange
        voice_file_mock = b"audio_data"
        transcribed_text = "Hello from audio"
        self.transcriber_mock.transcribe_audio.return_value = transcribed_text
        chat_mock = Mock()
        chat_mock.id = "test_id"  # Aseguramos que id es un string válido
        self.db_mock.get_chat.return_value = chat_mock
        chat_mock.get_conversation_history.return_value = ["history"]
        self.agent_mock.get_last_response.return_value = "response"

        # Act
        result = self.chat_service.continue_conversation("test_id", voice_file=voice_file_mock)

        # Assert
        self.transcriber_mock.transcribe_audio.assert_called_once_with(voice_file_mock)
        self.db_mock.get_chat.assert_called_once_with("test_id")
        self.agent_mock.set_memory_variables.assert_called_once_with(["history"])
        self.agent_mock.assert_called_once_with(query=transcribed_text)
        self.assertEqual(result, "response")


if __name__ == "__main__":
    unittest.main()