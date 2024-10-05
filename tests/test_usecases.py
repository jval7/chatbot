import unittest
from unittest.mock import Mock, patch
from app.services.usecases import ChatService, NoChatFound, InputNotProvided


class TestChatService(unittest.TestCase):

    def setUp(self):
        self.mock_agent = Mock()
        self.mock_db = Mock()
        self.mock_transcriber = Mock()

        # Crear instancia de ChatService
        self.chat_service = ChatService(
            agent=self.mock_agent,
            db=self.mock_db,
            transcriber=self.mock_transcriber
        )

    def test_start_conversation_when_calling_start_conversation_in_ChatService(self):
        # Arrange
        self.mock_db.save_chat = Mock()

        # Act
        conversation_id = self.chat_service.start_conversation()

        # Assert
        self.mock_db.save_chat.assert_called_once()
        self.assertIsNotNone(conversation_id)

    def test_continue_conversation_with_text_query_when_calling_continue_conversation_in_ChatService(self):
        # Arrange
        conversation_id = "12345"
        query = "Que es Dragon Ball?"
        mock_chat = Mock()
        mock_chat.id = "12345"

        self.mock_db.get_chat.return_value = mock_chat
        self.mock_agent.get_last_response.return_value = "Una serie de Anime"

        # Act:
        response = self.chat_service.continue_conversation(conversation_id=conversation_id, query=query)

        # Assert:
        self.mock_db.get_chat.assert_called_once_with(conversation_id)
        self.mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())
        self.mock_agent.assert_called_once_with(query=query)
        self.mock_agent.get_last_response.assert_called_once()
        self.assertEqual(response, "Una serie de Anime")


    @patch("requests.Session.post")
    def test_continue_conversation_with_voice_file_if_file_is_a_voice_file(self, mock_post):
        # Arrange
        conversation_id = "12345"
        voice_file = b"voice data"
        transcribed_text = "Que es Dragon Ball?"
        mock_chat = Mock()
        mock_chat.id = "12345"

        mock_response = Mock()
        mock_response.json.return_value = {"text": transcribed_text}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.mock_db.get_chat.return_value = mock_chat
        self.mock_agent.get_last_response.return_value = "Una serie de Anime"
        self.mock_transcriber.transcribe_audio.return_value = transcribed_text

        # Act
        response = self.chat_service.continue_conversation(conversation_id=conversation_id, voice_file=voice_file)

        # Assert
        self.mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
        self.mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())
        self.mock_agent.assert_called_once_with(query=transcribed_text)
        self.mock_agent.get_last_response.assert_called_once()
        self.assertEqual(response, "Una serie de Anime")

    def test_continue_conversation_if_no_chat_found(self):
        # Arrange
        self.mock_db.get_chat.return_value = None

        # Act, Assert
        with self.assertRaises(NoChatFound):
            self.chat_service.continue_conversation(conversation_id="12345", query="Hello")

    def test_continue_conversation_if_no_input_provided(self):
        # Act, Assert
        with self.assertRaises(InputNotProvided):
            self.chat_service.continue_conversation(conversation_id="12345")


    @patch("app.domain.models.Chat")
    def test_update_chat_when_calling_update_chat_in_ChatService(self, mock_chat_class):
        # Arrange
        mock_chat = Mock()
        mock_chat.id = "12345"
        mock_chat_class.return_value = mock_chat

        self.mock_agent.get_conversation_history.return_value = ["Pregunta", "Respuesta"]

        # Act
        self.chat_service._update_chat(mock_chat)

        # Assert
        self.mock_agent.get_conversation_history.assert_called_once()
        mock_chat.update_conversation.assert_called_once_with(["Pregunta", "Respuesta"])
        self.mock_db.save_chat.assert_called_once_with(mock_chat)
