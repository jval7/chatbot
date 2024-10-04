from unittest.mock import MagicMock,patch
import pytest

from app.services.usecases import ChatService,InputNotProvided,NoChatFound

from app.domain.models import Chat

from app.domain.ports import ChatRepository, AgentPort, TranscriptionPort


def test_start_conversation():

    mock_agent = MagicMock(spec=AgentPort)
    mock_db = MagicMock(spec=ChatRepository)
    mock_transcriber = MagicMock(spec=TranscriptionPort)


    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    chat_id = service.start_conversation()


    assert chat_id is not None  # Verificar que se haya retornado un chat_id
    mock_db.save_chat.assert_called_once()  # Asegurar que el método save_chat fue llamado una vez
    chat_saved = mock_db.save_chat.call_args[0][0]  # Extraer el objeto Chat guardado
    assert isinstance(chat_saved,Chat)  # Verificar que un objeto Chat fue guardado


def test_continue_conversation_with_voice_file():
    # Mocking de dependencias
    mock_agent = MagicMock(spec=AgentPort)
    mock_db = MagicMock(spec=ChatRepository)
    mock_transcriber = MagicMock(spec=TranscriptionPort)


    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    chat_instance = Chat(id="12345")


    mock_db.get_chat.return_value = chat_instance
    mock_transcriber.transcribe_audio.return_value = "transcribed text"
    mock_agent.get_last_response.return_value = "agent response"


    voice_file = b"dummy voice file"
    result = service.continue_conversation(conversation_id="12345", voice_file=voice_file)


    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)  # Verificar transcripción
    mock_db.get_chat.assert_called_once_with("12345")  # Verificar que se obtenga el chat correcto
    mock_agent.set_memory_variables.assert_called_once()  # Verificar que se llamen las variables de memoria
    mock_agent.assert_called_once_with(query="transcribed text")  # Verificar que el agente reciba el texto transcrito
    assert result == "agent response"  # Verificar que la respuesta del agente sea la esperada


def test_continue_conversation_with_query():
    # Mocking de dependencias
    mock_agent = MagicMock(spec=AgentPort)
    mock_db = MagicMock(spec=ChatRepository)
    mock_transcriber = MagicMock(spec=TranscriptionPort)


    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    chat_instance = Chat(id="12345")


    mock_db.get_chat.return_value = chat_instance
    mock_agent.get_last_response.return_value = "agent response"


    query = "test query"
    result = service.continue_conversation(conversation_id="12345", query=query)


    mock_transcriber.transcribe_audio.assert_not_called()  # No debe llamarse la transcripción
    mock_db.get_chat.assert_called_once_with("12345")  # Verificar que se obtenga el chat correcto
    mock_agent.set_memory_variables.assert_called_once()  # Verificar que se llamen las variables de memoria
    mock_agent.assert_called_once_with(query=query)  # Verificar que el agente reciba la query
    assert result == "agent response"  # Verificar que la respuesta del agente sea la esperada


def test_continue_conversation_no_input_provided():
    # Mocking de dependencias
    mock_agent = MagicMock(spec=AgentPort)
    mock_db = MagicMock(spec=ChatRepository)
    mock_transcriber = MagicMock(spec=TranscriptionPort)


    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    with pytest.raises(InputNotProvided):
        service.continue_conversation(conversation_id="12345")


def test_continue_conversation_no_chat_found():
    # Mocking de dependencias
    mock_agent = MagicMock(spec=AgentPort)
    mock_db = MagicMock(spec=ChatRepository)
    mock_transcriber = MagicMock(spec=TranscriptionPort)


    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    mock_db.get_chat.return_value = None


    with pytest.raises(NoChatFound):
        service.continue_conversation(conversation_id="invalid_id", query="test query")