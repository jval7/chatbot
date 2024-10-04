
import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain import models
from unittest.mock import Mock, patch


def test_update_chat():
    mock_agent = Mock()
    conversation_history = [
        {"type": "human", "content": "Hola"},
        {"type": "ai", "content": "Hola, ¿en qué puedo ayudarte?"}
    ]
    mock_agent.get_conversation_history.return_value = conversation_history

    mock_db = Mock()

    mock_transcriber = Mock()

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    chat = models.Chat(id="test_chat_id")

    chat_service._update_chat(chat)

    mock_agent.get_conversation_history.assert_called_once()

    expected_chat = models.Chat(id="test_chat_id")
    expected_chat.update_conversation(conversation_history)

    saved_chat = mock_db.save_chat.call_args[0][0]

    assert saved_chat.id == expected_chat.id
    assert saved_chat.conversation.history == expected_chat.conversation.history





def test_continue_conversation_with_query():
    mock_agent = Mock()
    mock_agent.get_last_response.return_value = "Respuesta del agente"
    mock_db = Mock()
    mock_transcriber = Mock()

    chat = models.Chat(id="test_chat_id")
    mock_db.get_chat.return_value = chat

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    response = chat_service.continue_conversation(
        conversation_id="test_chat_id",
        query="Hola",
        voice_file=None
    )

    mock_db.get_chat.assert_called_once_with("test_chat_id")
    mock_agent.set_memory_variables.assert_called_once_with(chat.get_conversation_history())
    mock_agent.assert_called_once_with(query="Hola")
    mock_db.save_chat.assert_called_once()
    assert response == "Respuesta del agente"


def test_continue_conversation_with_voice_file():
    mock_agent = Mock()
    mock_agent.get_last_response.return_value = "Respuesta del agente"
    mock_db = Mock()
    mock_transcriber = Mock()
    mock_transcriber.transcribe_audio.return_value = "Texto transcrito"

    chat = models.Chat(id="test_chat_id")
    mock_db.get_chat.return_value = chat

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    response = chat_service.continue_conversation(
        conversation_id="test_chat_id",
        query=None,
        voice_file=b"archivo de audio"
    )

    mock_transcriber.transcribe_audio.assert_called_once_with(b"archivo de audio")
    mock_db.get_chat.assert_called_once_with("test_chat_id")
    mock_agent.set_memory_variables.assert_called_once_with(chat.get_conversation_history())
    mock_agent.assert_called_once_with(query="Texto transcrito")
    mock_db.save_chat.assert_called_once()
    assert response == "Respuesta del agente"


def test_continue_conversation_no_input():
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    with pytest.raises(InputNotProvided) as exc_info:
        chat_service.continue_conversation(
            conversation_id="test_chat_id",
            query=None,
            voice_file=None
        )

    assert str(exc_info.value) == "No input provided"


def test_continue_conversation_chat_not_found():
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    mock_db.get_chat.return_value = None

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    with pytest.raises(NoChatFound) as exc_info:
        chat_service.continue_conversation(
            conversation_id="non_existent_chat_id",
            query="Hola",
            voice_file=None
        )

    assert str(exc_info.value) == "Chat not found"





def test_start_conversation():
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    with patch('app.services.usecases.logger') as mock_logger:
        chat_id = chat_service.start_conversation()

        mock_db.save_chat.assert_called_once()

        saved_chat = mock_db.save_chat.call_args[0][0]

        assert isinstance(saved_chat, models.Chat)

        assert chat_id == saved_chat.id

        mock_logger.info.assert_any_call("Saving chat")
        mock_logger.info.assert_any_call("Chat saved")
        assert mock_logger.info.call_count == 2
