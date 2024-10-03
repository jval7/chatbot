from unittest.mock import patch, Mock
import pytest
from app.domain import ports, models
from app.services.usecases import ChatService, InputNotProvided, NoChatFound


@patch("app.services.usecases.ChatService")
def test_start_conversation_initializes_new_chat_instance(mock_db_adapter=None):
    # Arrange
    mock_db_instance = mock_db_adapter.return_value
    mock_db_instance.save_chat.return_value = None
    mock_agent = Mock(spec=ports.AgentPort)
    mock_transcriber = Mock(spec=ports.TranscriptionPort)
    chat_service = ChatService(agent=mock_agent, db=mock_db_instance, transcriber=mock_transcriber)

    # Act
    result = chat_service.start_conversation()

    # Assert
    assert result is not None
    mock_db_instance.save_chat.assert_called_once()

@patch("app.domain.ports.AgentPort")
@patch("app.services.usecases.ChatService")
def test_update_chat_persists_conversation_history(mock_db_adapter, mock_agent):
    # Arrange
    mock_db_instance = mock_db_adapter.return_value
    mock_agent_instance = mock_agent.return_value
    mock_agent_instance.get_conversation_history.return_value = []

    chat = models.Chat(id="2221515")
    chat_service = ChatService(agent=mock_agent_instance, db=mock_db_instance, transcriber=Mock())

    # Act
    chat_service._update_chat(chat)

    # Assert
    mock_db_instance.save_chat.assert_called_once()
    saved_chat = mock_db_instance.save_chat.call_args[0][0]
    assert saved_chat.id == "2221515"
    assert saved_chat.get_conversation_history() == []


@patch("app.domain.ports.ChatRepository")
@patch("app.domain.ports.TranscriptionPort")
@patch("app.domain.ports.AgentPort")
def test_continue_conversation_processes_voice_input_and_generates_response(mock_agent, mock_transcriber, mock_db_adapter):
    # Arrange
    mock_db_instance = mock_db_adapter.return_value
    mock_agent_instance = mock_agent.return_value
    mock_transcriber_instance = mock_transcriber.return_value

    mock_db_instance.get_chat.return_value = models.Chat(id="2221341")
    mock_agent_instance.get_last_response.return_value = "response"
    mock_transcriber_instance.transcribe_audio.return_value = "query"

    chat_service = ChatService(agent=mock_agent_instance, db=mock_db_instance, transcriber=mock_transcriber_instance)

    # Act
    result = chat_service.continue_conversation("2221341", voice_file=b"voice file")

    # Assert
    assert result == "response"
    mock_transcriber_instance.transcribe_audio.assert_called_once_with(b"voice file")
    mock_db_instance.get_chat.assert_called_once_with("2221341")
    mock_agent_instance.set_memory_variables.assert_called_once()
    mock_agent_instance.assert_called_once_with(query="query")
    mock_db_instance.save_chat.assert_called_once()




def test_continue_conversation_raises_exception_on_missing_input():
    # Arrange
    chat_service = ChatService(agent=Mock(), db=Mock(), transcriber=Mock())

    # Act & Assert
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="2221515")

@patch("app.domain.ports.ChatRepository")
def test_continue_conversation_raises_exception_for_nonexistent_chat(mock_db_adapter):
    # Arrange
    mock_db_instance = mock_db_adapter.return_value
    mock_db_instance.get_chat.return_value = None

    chat_service = ChatService(agent=Mock(), db=mock_db_instance, transcriber=Mock())

    # Act & Assert
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="2221515", query="query")
