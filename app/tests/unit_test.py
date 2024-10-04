import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, NoChatFound, InputNotProvided
from app.domain import models


@pytest.fixture
def mock_agent():
    return Mock()


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def mock_transcriber():
    return Mock()


@pytest.fixture
def chat_service(mock_agent, mock_db, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


def test_start_conversation(chat_service, mock_db):
    # Ejecutar el método start_conversation
    chat_id = chat_service.start_conversation()

    # Verificar que se ha guardado un nuevo chat
    mock_db.save_chat.assert_called_once()

    # Verificar que el chat_id se ha generado y es de tipo string
    assert isinstance(chat_id, str)
    assert chat_id  # Verificar que no esté vacío


def test_continue_conversation_with_query(chat_service, mock_db, mock_agent):
    mock_db.get_chat.return_value = models.Chat(id="12345")
    mock_agent.get_last_response.return_value = "Respuesta del agente"

    response = chat_service.continue_conversation(conversation_id="12345", query="Hola")

    # Verificar que se ha llamado al método del agente con la query
    mock_agent.assert_called_once_with(query="Hola")

    # Verificar que se obtiene la respuesta correcta del agente
    assert response == "Respuesta del agente"


def test_continue_conversation_with_voice_file(chat_service, mock_db, mock_agent, mock_transcriber):
    mock_db.get_chat.return_value = models.Chat(id="12345")
    mock_agent.get_last_response.return_value = "Respuesta del agente"
    mock_transcriber.transcribe_audio.return_value = "Hola transcrito"

    response = chat_service.continue_conversation(conversation_id="12345", voice_file=b"archivo de voz")

    # Verificar que se ha transcrito el archivo de voz
    mock_transcriber.transcribe_audio.assert_called_once_with(b"archivo de voz")

    # Verificar que se ha llamado al método del agente con el texto transcrito
    mock_agent.assert_called_once_with(query="Hola transcrito")

    # Verificar que se obtiene la respuesta correcta del agente
    assert response == "Respuesta del agente"


def test_continue_conversation_updates_chat(chat_service, mock_db, mock_agent):
    # Configurar el mock para el chat existente
    chat = Mock()
    chat.id = "12345"
    chat.get_conversation_history.return_value = ["previous message"]
    mock_db.get_chat.return_value = chat

    # Configurar la respuesta del agente
    mock_agent.get_conversation_history.return_value = ["previous message", "new message"]
    mock_agent.get_last_response.return_value = "Respuesta del agente"

    # Parchear el método privado _update_chat para verificar si fue llamado
    chat_service._update_chat = Mock()

    # Ejecutar el método continue_conversation
    response = chat_service.continue_conversation(conversation_id="12345", query="Hola")

    # Verificar que _update_chat ha sido llamado
    chat_service._update_chat.assert_called_once_with(chat)

    # Verificar que la respuesta final es la esperada
    assert response == "Respuesta del agente"


def test_continue_conversation_no_chat_found(chat_service, mock_db):
    mock_db.get_chat.return_value = None

    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="99999", query="Hola")


def test_continue_conversation_no_input_provided(chat_service):
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="12345")



