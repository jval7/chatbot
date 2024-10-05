import unittest
from unittest.mock import patch, Mock

from langchain_core import language_models
from langchain_core.messages import HumanMessage, AIMessage

from app.adapters import ToolConfig, Agent
from app.adapters.audio_transcription import OpenAITranscriptionClient
from app.domain.models import Chat, Conversation
from app.adapters.chat_repository import InMemoryChatRepository


class TestOpenAITranscriptionClient(unittest.TestCase):
    @patch('requests.Session.post')
    def test_transcribe_audio_success(self, mock_post):
        # Arrange
        api_key = "test_api_key"
        api_url = "https://api.openai.com/v1/audio/transcriptions"
        transcription_model = "whisper-1"
        audio_file = b"audio data"

        mock_response = Mock()
        mock_response.json.return_value = {"text": "Texto transcrito"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Instanciar el cliente
        client = OpenAITranscriptionClient(api_key, api_url, transcription_model)

        # Act
        result = client.transcribe_audio(audio_file)

        # Assert
        mock_post.assert_called_once()
        self.assertEqual(result, "Texto transcrito")

    @patch('requests.Session.post')
    def test_transcribe_audio_failure(self, mock_post):
        # Arrange
        api_key = "test_api_key"
        api_url = "https://api.openai.com/v1/audio/transcriptions"
        transcription_model = "whisper-1"
        audio_file = b"audio data"

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Error de transcripción")
        mock_post.return_value = mock_response

        # Instanciar el cliente
        client = OpenAITranscriptionClient(api_key, api_url, transcription_model)

        # Act, Assert
        with self.assertRaises(Exception) as context:
            client.transcribe_audio(audio_file)

        self.assertEqual(str(context.exception),
                         "Error de transcripción")



class TestInMemoryChatRepository(unittest.TestCase):
    def setUp(self):
        self.chat_repository = InMemoryChatRepository()

    def test_save_chat_success(self):
        # Arrange
        conversation_history = [HumanMessage(content="Hola"), AIMessage(content="¿Cómo estás?")]
        conversation = Conversation(history=conversation_history)
        chat = Chat(id="12345", conversation=conversation)
        self.chat_repository.save_chat(chat)

        # Act
        retrieved_chat = self.chat_repository.get_chat("12345")

        # Assert
        self.assertIsNotNone(retrieved_chat)
        self.assertEqual(retrieved_chat.id, "12345")
        self.assertEqual(retrieved_chat.conversation.history, conversation_history)

    def test_get_chat_not_found(self):
        # Act
        chat = self.chat_repository.get_chat("non_existent_id")

        # Assert
        self.assertIsNone(chat)

    def test_get_chat_success(self):
        # Arrange
        conversation_history = [HumanMessage(content="Hola"), AIMessage(content="¿Cómo estás?")]
        conversation = Conversation(history=conversation_history)
        chat = Chat(id="12345", conversation=conversation)
        self.chat_repository.save_chat(chat)

        # Act
        retrieved_chat = self.chat_repository.get_chat("12345")

        # Assert
        self.assertIsNotNone(retrieved_chat)
        self.assertEqual(retrieved_chat.id, "12345")
        self.assertEqual(retrieved_chat.conversation.history, conversation_history)


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock(spec=language_models.BaseChatModel)

        self.tools = [
            ToolConfig(name="tool1", func=Mock(return_value="result1"), description="Descripción de tool1"),
            ToolConfig(name="tool2", func=Mock(return_value="result2"), description="Descripción de tool2"),
        ]

        # Inicializar el agente
        self.agent = Agent(tools=self.tools, llm=self.mock_llm, memory_key="test_memory")

    def test_agent_call(self):

        # Arrange
        query = "¿Cómo estás?"
        expected_response = {"output": "respuesta de prueba"}

        self.agent._agent = Mock(return_value=expected_response)

        # Act
        response = self.agent(query)

        # Assert
        self.agent._agent.assert_called_once_with(query)
        self.assertEqual(response, expected_response)

    def test_get_conversation_history_empty(self):
        # Act
        history = self.agent.get_conversation_history()

        # Assert
        self.assertEqual(history, [])

    def test_set_memory_variables(self):
        # Arrange
        mock_history = [Mock(spec=AIMessage), Mock(spec=AIMessage)]

        # Act
        self.agent.set_memory_variables(mock_history)

        # Assert
        self.assertEqual(len(self.agent._memory.chat_memory.messages), len(mock_history))

    def test_get_last_response(self):
        # Arrange
        mock_response = Mock(content="Última respuesta")
        self.agent._memory.chat_memory.messages.append(mock_response)

        # Act
        last_response = self.agent.get_last_response()

        # Assert
        self.assertEqual(last_response, "Última respuesta")
