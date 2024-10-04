from typing import List
from unittest.mock import Mock, MagicMock
from app.services import usecases
from app.domain import ports,models
from app.services.usecases import NoChatFound, InputNotProvided
import pytest

########### SEGUNDO PARCIAL - PRUEBAS UNITARIAS ######################

@pytest.fixture
def mock_agent():
    agent = Mock(spec=ports.AgentPort)
    return agent

@pytest.fixture
def mock_db():
    db = Mock(spec=ports.ChatRepository)
    return db

@pytest.fixture
def mock_transcriber():
    transcriber = Mock(spec=ports.TranscriptionPort)
    return transcriber

@pytest.fixture
def test_chat_service(mock_agent, mock_db, mock_transcriber):
    return usecases.ChatService(mock_agent, mock_db, mock_transcriber)

def test_should_start_conversation(test_chat_service,mock_db):
    # Arrange
    mock_chat = MagicMock()
    mock_chat.id = "161124"
    models.Chat = MagicMock(return_value=mock_chat)

    # Act
    chat_id = test_chat_service.start_conversation()
    mock_db.save_chat.assert_called_once_with(mock_chat)
    # Assert
    assert chat_id == "161124"

def test_should_continue_conversation_with_query(test_chat_service, mock_agent, mock_db):
    # Arrange
    conversation_id = "mock_chat_id"
    query = "Twinkle, twinkle, little star"

    chat_model = MagicMock()
    chat_model.id = conversation_id
    chat_model.get_conversation_history.return_value=[]

    mock_db.get_chat.return_value = chat_model
    mock_agent.get_last_response.return_value="How I wonder what you are"

    # Act
    response = test_chat_service.continue_conversation(conversation_id,query=query)

    # Assert
    mock_db.get_chat.assert_called_once_with(conversation_id)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    assert response == "How I wonder what you are" #Para comparar el valor de retorno

# Prueba para el caso en que se proporciona un archivo de voz (voice_file)
def test_should_continue_conversation_with_voice_file(test_chat_service, mock_agent, mock_db, mock_transcriber):
    # Arrange
    conversation_id = "mock_chat_id"
    voice_file = b"mock_voice_data"
    transcribed_text = "Twinkle, twinkle, little star"

    chat_model = MagicMock()
    chat_model.id = conversation_id
    chat_model.get_conversation_history.return_value = []

    mock_db.get_chat.return_value = chat_model
    mock_transcriber.transcribe_audio.return_value = transcribed_text
    mock_agent.get_last_response.return_value = "How I wonder what you are"

    # Act
    response = test_chat_service.continue_conversation(conversation_id, voice_file=voice_file)

    # Assert
    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
    mock_db.get_chat.assert_called_once_with(conversation_id)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=transcribed_text)
    assert response == "How I wonder what you are"


# Prueba para el caso en que no se proporciona ni query ni voice_file
def test_should_raise_input_not_provided(test_chat_service):
    # Arrange
    conversation_id = "mock_chat_id"

    # Act & Assert
    with pytest.raises(InputNotProvided):
        test_chat_service.continue_conversation(conversation_id)


# Prueba para el caso en que no se encuentra el chat
def test_should_raise_no_chat_found(test_chat_service, mock_db):
    # Arrange
    conversation_id = "non_existing_chat_id"
    query = "Twinkle, twinkle, little star"

    mock_db.get_chat.return_value = None

    # Act & Assert
    with pytest.raises(NoChatFound):
        test_chat_service.continue_conversation(conversation_id, query=query)

def test_should_update_chat_when_calling_update_chat_method(test_chat_service, mock_agent, mock_db):
    # Arrange
    mock_chat = MagicMock()
    mock_chat.id = "161124"
    mock_conversation_history = ["If you are happy and you know it, clap your hands", "Clap, clap!"]

    mock_agent.get_conversation_history = MagicMock(return_value=mock_conversation_history)
    models.Chat = MagicMock()

    # Act
    test_chat_service._update_chat(mock_chat)

    # Assert
    models.Chat.assert_called_once_with(id=mock_chat.id)
    new_chat=models.Chat.return_value
    new_chat.update_conversation.assert_called_once_with(mock_conversation_history)
    mock_db.save_chat.assert_called_once_with(new_chat)


