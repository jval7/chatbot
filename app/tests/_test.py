import unittest
from unittest.mock import Mock, patch
from app.domain import ports
from app.services.usecases import ChatService, NoChatFound, InputNotProvided


class TestChatService(unittest.TestCase):

    def setUp(self):
        # Arrange: Se crean los mocks para los puertos y dependencias
        self.mock_agent = Mock(spec=ports.AgentPort)
        self.mock_db = Mock(spec=ports.ChatRepository)
        self.mock_transcriber = Mock(spec=ports.TranscriptionPort)
        self.chat_service = ChatService(
            agent=self.mock_agent,
            db=self.mock_db,
            transcriber=self.mock_transcriber
        )

    @patch('app.domain.models.Chat')
    def test_should_start_conversation_when_chat_is_started(self, MockChat):
        # Arrange: Preparar el modelo de chat y el comportamiento del mock
        mock_chat_instance = MockChat.return_value
        mock_chat_instance.id = "test_chat_id"  # Simulamos el ID esperado

        # Act: Iniciar la conversación
        chat_id = self.chat_service.start_conversation()

        # Assert: Comprobar que el chat se guardó y se devolvió el ID correcto
        self.mock_db.save_chat.assert_called_once_with(mock_chat_instance)
        self.assertEqual(chat_id, "test_chat_id")

    @patch('app.domain.models.Chat')
    def test_should_continue_conversation_when_query_is_provided(self, MockChat):
        # Arrange: Preparar el historial de conversación y comportamiento del mock
        chat_id = "12345"
        query = "Hello, how are you?"
        mock_chat = MockChat.return_value
        mock_chat.id = chat_id
        mock_chat.get_conversation_history.return_value = ["Hi"]
        self.mock_db.get_chat.return_value = mock_chat
        self.mock_agent.get_last_response.return_value = "I'm good, thank you!"

        # Act: Continuar la conversación con un query de texto
        response = self.chat_service.continue_conversation(conversation_id=chat_id, query=query)

        # Assert: Comprobar que se obtuvieron los resultados correctos
        self.mock_db.get_chat.assert_called_once_with(chat_id)
        self.mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())
        self.mock_agent.assert_called_once_with(query=query)
        self.assertEqual(response, "I'm good, thank you!")

    @patch('app.domain.models.Chat')
    def test_should_continue_conversation_when_voice_file_is_provided(self, MockChat):
        # Arrange: Preparar el comportamiento del transcriptor y el agente
        chat_id = "12345"
        voice_file = b"voice data"
        transcribed_text = "Hello from the voice file"
        mock_chat = MockChat.return_value
        mock_chat.id = chat_id
        mock_chat.get_conversation_history.return_value = ["Hi"]
        self.mock_db.get_chat.return_value = mock_chat
        self.mock_transcriber.transcribe_audio.return_value = transcribed_text
        self.mock_agent.get_last_response.return_value = "Voice transcribed!"

        # Act: Continuar la conversación con un archivo de voz
        response = self.chat_service.continue_conversation(conversation_id=chat_id, voice_file=voice_file)

        # Assert: Verificar que la transcripción y la conversación se procesaron correctamente
        self.mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
        self.mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())
        self.mock_agent.assert_called_once_with(query=transcribed_text)
        self.assertEqual(response, "Voice transcribed!")

    def test_should_raise_error_when_no_input_is_provided(self):
        # Arrange: No se proporciona ni query ni archivo de voz
        chat_id = "12345"

        # Act & Assert: Verificar que se lanza la excepción adecuada
        with self.assertRaises(InputNotProvided):
            self.chat_service.continue_conversation(conversation_id=chat_id)

    def test_should_raise_error_when_chat_is_not_found(self):
        # Arrange: No se encuentra el chat en la base de datos
        chat_id = "12345"
        self.mock_db.get_chat.return_value = None

        # Act & Assert: Verificar que se lanza la excepción adecuada
        with self.assertRaises(NoChatFound):
            self.chat_service.continue_conversation(conversation_id=chat_id, query="Hello")


if __name__ == "_main_":
    unittest.main()