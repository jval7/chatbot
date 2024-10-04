import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, models, InputNotProvided, NoChatFound

# Mocks
@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.get_last_response.return_value = "respuesta del query"
    agent.get_conversation_history.return_value = ["query", "respuesta del query"]
    return agent

@pytest.fixture
def mock_data_base():
    db = Mock()
    db.get_chat.return_value = models.Chat(id="id_conversation")
    return db

@pytest.fixture
def mock_transcriber():
    transcriber = Mock()
    transcriber.transcribe_audio.return_value = "query transcrito"
    return transcriber

@pytest.fixture
def chat_service(mock_agent, mock_data_base, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_data_base, transcriber=mock_transcriber)

# Tests
def test_should_start_conversation_when_start_conversation_is_called(chat_service, mock_data_base):
    result = chat_service.start_conversation()

    assert result is not None
    mock_data_base.save_chat.assert_called_once()

def test_should_raise_error_when_start_conversation_fails_to_save(chat_service, mock_data_base):
    mock_data_base.save_chat.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        chat_service.start_conversation()

    assert str(exc_info.value) == "Database error"
    mock_data_base.save_chat.assert_called_once()

def test_should_continue_conversation_when_text_is_provided(chat_service, mock_data_base, mock_agent):
    result = chat_service.continue_conversation(conversation_id="id_conversation", query="Hey!!")

    assert result == "respuesta del query"
    mock_data_base.get_chat.assert_called_once_with("id_conversation")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="Hey!!")

def test_should_continue_conversation_when_voice_is_provided(chat_service, mock_data_base, mock_agent, mock_transcriber):
    file = b"Audio"
    result = chat_service.continue_conversation(conversation_id="id_conversation", voice_file=file)

    assert result == "respuesta del query"
    mock_transcriber.transcribe_audio.assert_called_once_with(file)
    mock_data_base.get_chat.assert_called_once_with("id_conversation")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="query transcrito")

def test_should_raise_error_when_voice_file_is_none(chat_service):
    with pytest.raises(InputNotProvided) as exc_info:
        chat_service.continue_conversation(conversation_id="conversation_id", voice_file=None)

    assert str(exc_info.value) == "No input provided"

def test_should_raise_error_when_no_input_is_provided(chat_service):
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="id_conversation")

def test_should_raise_error_when_chat_is_not_found(chat_service, mock_data_base):
    mock_data_base.get_chat.return_value = None
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="id_invalido", query="Hey!!")