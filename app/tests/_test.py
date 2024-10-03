from unittest import mock
import pytest
from app.domain import ports, models
from app.services.usecases import ChatService, NoChatFound, InputNotProvided

def test_start_conversation():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)

    # Act
    conversation_id = chat_service.start_conversation()

    # Assert
    assert isinstance(conversation_id, str)
    db_mock.save_chat.assert_called_once()
    saved_chat = db_mock.save_chat.call_args[0][0]
    assert isinstance(saved_chat, models.Chat)
    assert saved_chat.id == conversation_id

def test_continue_conversation_with_query():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)

    conversation_id = 'test_conversation_id'
    query = 'Hola, ¿cómo estás?'

    chat_mock = mock.Mock(spec=models.Chat)
    chat_mock.get_conversation_history.return_value = []
    chat_mock.id = conversation_id
    db_mock.get_chat.return_value = chat_mock

    agent_mock.get_last_response.return_value = 'Estoy bien, gracias.'
    conversation_history = ['User: Hola, ¿cómo estás?', 'Agent: Estoy bien, gracias.']
    agent_mock.get_conversation_history.return_value = conversation_history

    # Act
    response = chat_service.continue_conversation(conversation_id=conversation_id, query=query)

    # Assert
    db_mock.get_chat.assert_called_with(conversation_id)
    agent_mock.set_memory_variables.assert_called_with([])
    agent_mock.assert_called_with(query=query)
    assert response == 'Estoy bien, gracias.'
    db_mock.save_chat.assert_called()
    saved_chat = db_mock.save_chat.call_args[0][0]
    assert saved_chat.id == conversation_id
    assert saved_chat.get_conversation_history() == conversation_history


def test_continue_conversation_with_voice_file():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)

    conversation_id = 'test_conversation_id'
    voice_file = b'voice data'
    transcribed_text = 'Hola desde archivo de voz.'

    transcriber_mock.transcribe_audio.return_value = transcribed_text

    chat_mock = mock.Mock(spec=models.Chat)
    chat_mock.get_conversation_history.return_value = []
    chat_mock.id = conversation_id
    db_mock.get_chat.return_value = chat_mock

    agent_mock.get_last_response.return_value = 'Estoy bien, gracias.'
    conversation_history = ['User: Hola desde archivo de voz.', 'Agent: Estoy bien, gracias.']
    agent_mock.get_conversation_history.return_value = conversation_history

    # Act
    response = chat_service.continue_conversation(conversation_id=conversation_id, voice_file=voice_file)

    # Assert
    transcriber_mock.transcribe_audio.assert_called_with(voice_file)
    db_mock.get_chat.assert_called_with(conversation_id)
    agent_mock.set_memory_variables.assert_called_with([])
    agent_mock.assert_called_with(query=transcribed_text)
    assert response == 'Estoy bien, gracias.'
    db_mock.save_chat.assert_called()
    saved_chat = db_mock.save_chat.call_args[0][0]
    assert saved_chat.get_conversation_history() == conversation_history



def test_continue_conversation_no_input():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    conversation_id = 'test_conversation_id'

    # Act and Assert
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id=conversation_id)


def test_continue_conversation_invalid_conversation_id():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    conversation_id = 'invalid_conversation_id'
    query = 'Hola, ¿cómo estás?'

    # Mock de chat no existente
    db_mock.get_chat.return_value = None

    # Act and Assert
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id=conversation_id, query=query)


def test_continue_conversation_with_query_and_voice_file():
    # Arrange
    agent_mock = mock.Mock(spec=ports.AgentPort)
    db_mock = mock.Mock(spec=ports.ChatRepository)
    transcriber_mock = mock.Mock(spec=ports.TranscriptionPort)

    chat_service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    conversation_id = 'test_conversation_id'
    voice_file = b'voice data'
    transcribed_text = 'Hola desde archivo de voz.'
    query = 'Hola desde archivo de voz.'

    # Mock de transcripción
    transcriber_mock.transcribe_audio.return_value = transcribed_text

    # Mock de chat existente
    chat_mock = mock.Mock(spec=models.Chat)
    chat_mock.get_conversation_history.return_value = []
    chat_mock.id = conversation_id
    db_mock.get_chat.return_value = chat_mock

    # Configuración del agente
    agent_mock.get_last_response.return_value = 'Response to voice input.'
    conversation_history = ['User: Hola, ¿cómo estás?', 'Agent: Estoy bien, gracias.']
    agent_mock.get_conversation_history.return_value = conversation_history

    # Act
    response = chat_service.continue_conversation(conversation_id=conversation_id, query=query, voice_file=voice_file)

    # Assert
    transcriber_mock.transcribe_audio.assert_called_with(voice_file)
    agent_mock.assert_called_with(query=transcribed_text)
    assert response == 'Response to voice input.'
    db_mock.save_chat.assert_called()
