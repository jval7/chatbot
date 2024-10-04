from unittest.mock import Mock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain.models import Chat, Conversation
from app.domain.ports import ChatRepository, AgentPort, TranscriptionPort
from langchain_core.messages import ai
import pytest


def test_start_conversation():
    # Setup
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Execution
    chat_id = chat_service.start_conversation()

    # Assert
    assert isinstance(chat_id, str)
    mock_db.save_chat.assert_called_once()


def test_update_conversation():
    # Setup
    chat = Chat()
    new_messages = [ai.AIMessage(content="Test message")]

    # Execution
    chat.update_conversation(new_messages)

    # Assert
    assert chat.get_conversation_history() == new_messages


def test_get_conversation_history():
    # Setup
    chat = Chat()
    expected_history = [ai.AIMessage(content="Hello!")]

    # Execution
    chat.update_conversation(expected_history)
    history = chat.get_conversation_history()

    # Assert
    assert history == expected_history


def test_continue_conversation_with_audio():
    # Setup
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_id = "test_chat_id"
    voice_file = b"audio_data"

    # Simulación de un chat existente
    mock_chat = Mock()
    mock_chat.get_conversation_history.return_value = []
    mock_chat.id = chat_id
    mock_db.get_chat.return_value = mock_chat

    # Definir lo que devuelve el transcriptor
    mock_transcriber.transcribe_audio.return_value = "Transcribed text"
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Execution
    response = chat_service.continue_conversation(conversation_id=chat_id, voice_file=voice_file)

    # Assert
    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query="Transcribed text")
    mock_db.save_chat.assert_called_once()
    assert response is not None  # Asegúrate de que haya una respuesta


def test_continue_conversation_no_chat_found():
    # Setup
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Simular que no se encuentra el chat
    mock_db.get_chat.return_value = None

    # Execution & Assert
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation("non_existent_chat_id")


def test_continue_conversation_with_query():
    # Setup
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Simular un chat existente
    chat_id = "test_chat_id"
    mock_chat = Mock()
    mock_chat.get_conversation_history.return_value = []
    mock_chat.id = chat_id  # Asegúrate de que el id sea una cadena
    mock_db.get_chat.return_value = mock_chat
    query = "Hello!"

    # Execution
    response = chat_service.continue_conversation(conversation_id=chat_id, query=query)

    # Assert
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    mock_db.save_chat.assert_called_once()
    assert response is not None  # Asegúrate de que haya una respuesta

class TestChatRepository:
    def test_save_chat(self):
        # Setup
        mock_repository = Mock(ChatRepository)
        mock_chat = Mock(spec=Chat)

        # Execution
        mock_repository.save_chat(mock_chat)

        # Assert
        mock_repository.save_chat.assert_called_once_with(mock_chat)

    def test_get_chat(self):
        # Configuration
        mock_repository = Mock(ChatRepository)
        mock_chat = Mock(spec=Chat)
        mock_repository.get_chat.return_value = mock_chat

        # Execution
        chat = mock_repository.get_chat("chat_id_123")

        # Assert
        assert chat == mock_chat
        mock_repository.get_chat.assert_called_once_with("chat_id_123")

    def test_get_chat_none(self):
        # Setup
        mock_repository = Mock(ChatRepository)
        mock_repository.get_chat.return_value = None

        # Execution
        chat = mock_repository.get_chat("non_existent_chat_id")

        # Assert
        assert chat is None
        mock_repository.get_chat.assert_called_once_with("non_existent_chat_id")


class TestAgentPort:
    def test_set_memory_variables(self):
        # Setup
        mock_agent = Mock(AgentPort)
        history = [ai.BaseMessage(type="user", content="Hello"), ai.BaseMessage(type="user", content="Hi!")]

        # Execution
        mock_agent.set_memory_variables(history)

        # Assert
        mock_agent.set_memory_variables.assert_called_once_with(history)

    def test_agent_call(self):
        # Configuration
        mock_agent = Mock(AgentPort)

        # Simular el comportamiento del método __call__ del mock
        mock_agent.side_effect = lambda query: {"response": "Hello, how can I help you?"}

        # Execution
        response = mock_agent("Hello")

        # Assert
        assert response == {"response": "Hello, how can I help you?"}
        mock_agent.assert_called_once_with("Hello")

    def test_get_conversation_history(self):
        # Setup
        mock_agent = Mock(AgentPort)
        history = [ai.BaseMessage(type="user", content="Hello"), ai.BaseMessage(type="user", content="Hi!")]
        mock_agent.get_conversation_history.return_value = history

        # Execution
        retrieved_history = mock_agent.get_conversation_history()

        # Assert
        assert retrieved_history == history
        mock_agent.get_conversation_history.assert_called_once()

    def test_get_last_response(self):
        # Setup
        mock_agent = Mock(AgentPort)
        mock_agent.get_last_response.return_value = "Goodbye!"

        # Execution
        response = mock_agent.get_last_response()

        # Assert
        assert response == "Goodbye!"
        mock_agent.get_last_response.assert_called_once()

