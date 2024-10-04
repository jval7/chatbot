import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain.ports import ChatRepository, TranscriptionPort
from app.domain import models
from langchain_core.messages import ai

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

# Tests principales para el servicio
def test_start_conversation(chat_service, mock_db):
    mock_db.save_chat.return_value = None
    result = chat_service.start_conversation()

    assert result is not None
    mock_db.save_chat.assert_called_once()

def test_continue_conversation_with_text_when_query_sended(chat_service, mock_db, mock_agent):
    result = chat_service.continue_conversation(conversation_id="conversation_id", query="Buenas tardes profe")

    assert result == "response"
    mock_db.get_chat.assert_called_once_with("conversation_id")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="Buenas tardes profe")

def test_continue_conversation_with_voice(chat_service, mock_db, mock_agent, mock_transcriber):
    voice_file = b"voice data"
    result = chat_service.continue_conversation(conversation_id="conversation_id", voice_file=voice_file)

    assert result == "response"
    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
    mock_db.get_chat.assert_called_once_with("conversation_id")
    mock_agent.set_memory_variables.assert_called_once()
    mock_agent.assert_called_once_with(query="transcribed query")

def test_continue_conversation_no_input(chat_service):
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="conversation_id")


def test_continue_conversation_chat_not_found(chat_service, mock_db):
    mock_db.get_chat.return_value = None
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="invalid_id", query="Hello")


def test_continue_conversation_transcription_error(chat_service, mock_transcriber):
    voice_file = b"invalid voice data"
    mock_transcriber.transcribe_audio.side_effect = Exception("Transcription failed")
    
    with pytest.raises(Exception, match="Transcription failed"):
        chat_service.continue_conversation(conversation_id="conversation_id", voice_file=voice_file)

    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)


def test_chat_repository():
    mock_repo = Mock(spec=ChatRepository)
    
    chat = models.Chat(id="chat_id")
    mock_repo.save_chat(chat)
    mock_repo.save_chat.assert_called_once_with(chat)

    mock_repo.get_chat.return_value = chat
    result = mock_repo.get_chat("chat_id")
    assert result == chat
    mock_repo.get_chat.assert_called_once_with("chat_id")


def test_transcription_port():    
    mock_transcriber = Mock(spec=TranscriptionPort)

    mock_transcriber.transcribe_audio.return_value = "Transcribed text"
    audio_file = b"audio data"
    transcription = mock_transcriber.transcribe_audio(audio_file)
    assert transcription == "Transcribed text"
    mock_transcriber.transcribe_audio.assert_called_once_with(audio_file)
