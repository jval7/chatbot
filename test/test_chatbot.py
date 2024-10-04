import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, models, InputNotProvided, NoChatFound

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.get_last_response.return_value = "response"
    agent.get_conversation_history.return_value = ["query", "response"]
    return agent

@pytest.fixture
def mock_db():
    db = Mock()
    db.get_chat.return_value = models.Chat(id="conversation_id")
    return db

@pytest.fixture
def mock_transcriber():
    transcriber = Mock()
    transcriber.transcribe_audio.return_value = "transcribed query"
    return transcriber

@pytest.fixture
def chat_service(mock_agent, mock_db, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

def test_initializer_conversation_chatbot(chat_service, mock_db):
    mock_db.save_chat.return_value = None
    result = chat_service.start_conversation()

    assert result is not None
    mock_db.save_chat.assert_called_once()

def test_still_in_the_text_conversation(chat_service, mock_db, mock_agent):
    result = chat_service.continue_conversation(conversation_id="conversation_id", query="Hello")

    assert result == "response"
    mock_db.get_chat.assert_called_once_with("conversation_id")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="Hello")

def test_still_in_the_text_voice(chat_service, mock_db, mock_agent, mock_transcriber):
    voice_file = b"voice data"
    result = chat_service.continue_conversation(conversation_id="conversation_id", voice_file=voice_file)

    assert result == "response"
    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
    mock_db.get_chat.assert_called_once_with("conversation_id")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="transcribed query")

def test_still_in_the_conversation_without_input(chat_service):
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="conversation_id")

def test_still_in_the_conversation_without_chat_found(chat_service, mock_db):
    mock_db.get_chat.return_value = None
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="invalid_id", query="Hello")