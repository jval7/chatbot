import unittest
from unittest.mock import MagicMock
from app.services.usecases import ChatService, NoChatFound, InputNotProvided
from app.domain import models
from app.logs import logger


class TestChatService(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.agent = MagicMock()
        self.db = MagicMock()
        self.transcriber = MagicMock()

        # Crear instancia de ChatService con mocks
        self.chat_service = ChatService(
            agent=self.agent,
            db=self.db,
            transcriber=self.transcriber
        )

    def test_start_conversation(self):
        # Simular el comportamiento de la base de datos
        chat_mock = MagicMock(spec=models.Chat)
        chat_mock.id = "12345"
        models.Chat = MagicMock(return_value=chat_mock)

        # Llamar al metodo start_conversation
        conversation_id = self.chat_service.start_conversation()

        # Asegurarse de que se creó el chat y se guardó
        models.Chat.assert_called_once()
        self.db.save_chat.assert_called_once_with(chat_mock)

        # Verificar que el ID devuelto es el correcto
        self.assertEqual(conversation_id, "12345")

    def test_continue_conversation_with_text_query(self):
        # Simular que existe una conversación
        chat_mock = MagicMock(spec=models.Chat)
        chat_mock.get_conversation_history.return_value = []

        # Asignar un valor al atributo 'id' del chat_mock
        chat_mock.id = "12345"

        self.db.get_chat.return_value = chat_mock

        # Llamar al metodo continue_conversation con un query de texto
        response = self.chat_service.continue_conversation(conversation_id="12345", query="Hello")

        # Asegurarse de que se recuperó el chat y se procesó el query
        self.db.get_chat.assert_called_once_with("12345")
        self.agent.set_memory_variables.assert_called_once_with([])
        self.agent.assert_called_once_with(query="Hello")

        # Verificar que se guarda un nuevo Chat con los atributos esperados
        self.db.save_chat.assert_called_once()

        # Obtener el argumento pasado a save_chat
        saved_chat = self.db.save_chat.call_args[0][0]

        # Verificar que el nuevo chat tenga el mismo id y el historial actualizado
        self.assertEqual(saved_chat.id, "12345")
        self.assertIsInstance(saved_chat.conversation, models.Conversation)

        # Verificar que el último response del agente fue retornado
        self.agent.get_last_response.assert_called_once()
        self.assertEqual(response, self.agent.get_last_response())

    def test_continue_conversation_with_voice_file(self):
        # Simular que existe una conversación
        chat_mock = MagicMock(spec=models.Chat)
        chat_mock.get_conversation_history.return_value = []

        # Asignar un valor al atributo 'id' del chat_mock
        chat_mock.id = "12345"

        self.db.get_chat.return_value = chat_mock

        # Simular transcripción de audio
        self.transcriber.transcribe_audio.return_value = "Hello from voice"

        # Llamar al metodo continue_conversation con un archivo de voz
        voice_file = b"fake audio bytes"
        response = self.chat_service.continue_conversation(conversation_id="12345", voice_file=voice_file)

        # Asegurarse de que se recuperó el chat y se transcribió el archivo de voz
        self.db.get_chat.assert_called_once_with("12345")
        self.transcriber.transcribe_audio.assert_called_once_with(voice_file)
        self.agent.set_memory_variables.assert_called_once_with([])
        self.agent.assert_called_once_with(query="Hello from voice")

        # Verificar que se guarda un nuevo Chat con los atributos esperados
        self.db.save_chat.assert_called_once()

        # Obtener el argumento pasado a save_chat
        saved_chat = self.db.save_chat.call_args[0][0]

        # Verificar que el nuevo chat tenga el mismo id y el historial actualizado
        self.assertEqual(saved_chat.id, "12345")
        self.assertIsInstance(saved_chat.conversation, models.Conversation)

        # Verificar que el último response del agente fue retornado
        self.agent.get_last_response.assert_called_once()
        self.assertEqual(response, self.agent.get_last_response())

    def test_continue_conversation_raises_no_chat_found(self):
        # Simular que no existe la conversación
        self.db.get_chat.return_value = None

        # Asegurarse de que se lanza la excepción correcta
        with self.assertRaises(NoChatFound):
            self.chat_service.continue_conversation(conversation_id="invalid_id", query="Hello")

    def test_continue_conversation_raises_input_not_provided(self):
        # Simular que existe una conversación
        chat_mock = MagicMock(spec=models.Chat)
        self.db.get_chat.return_value = chat_mock

        # Asegurarse de que se lanza la excepción correcta cuando no hay entrada
        with self.assertRaises(InputNotProvided):
            self.chat_service.continue_conversation(conversation_id="12345")


if __name__ == "__main__":
    unittest.main()