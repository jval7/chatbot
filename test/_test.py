from unittest.mock import Mock, MagicMock, patch
import pytest
from app.domain import ports
from app.services import usecases
from app.services.usecases import NoChatFound, InputNotProvided
from app.domain.models import Chat, generate_uuid, Conversation
from langchain_core.messages import ai, human

@pytest.fixture
def mock_agente():
    return Mock(spec=ports.AgentPort)

@pytest.fixture
def mock_bd():
    return Mock(spec=ports.ChatRepository)

@pytest.fixture
def mock_transcriptor():
    return Mock(spec=ports.TranscriptionPort)

@pytest.fixture
def servicio_chat(mock_agente, mock_bd, mock_transcriptor):
    return usecases.ChatService(mock_agente, mock_bd, mock_transcriptor)

def test_iniciar_conversacion(servicio_chat, mock_bd):
    with patch('app.domain.models.Chat', return_value=MagicMock(id="777")) as mock_chat:
        resultado = servicio_chat.start_conversation()
        mock_bd.save_chat.assert_called_once_with(mock_chat.return_value)
        assert resultado == "777"

def test_continuar_conversacion(servicio_chat, mock_bd, mock_agente):
    with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:
        id_conversacion = "777"
        consulta = "¿Qué tal?"
        mock_chat.return_value.get_conversation_history.return_value = []
        mock_bd.get_chat.return_value = mock_chat.return_value
        mock_agente.get_last_response.return_value = "Hola, ¿cómo estás?"
        resultado = servicio_chat.continue_conversation(id_conversacion, consulta)
        mock_bd.get_chat.assert_called_once_with(id_conversacion)
        mock_agente.set_memory_variables.assert_called_once_with([])
        mock_agente.get_last_response.assert_called_once()
        mock_agente.get_conversation_history.assert_called_once()
        mock_bd.save_chat.assert_called_once()
        assert resultado == "Hola, ¿cómo estás?"

def test_id_conversacion_invalido(servicio_chat, mock_bd):
    id_conversacion = "789"
    consulta = "¿Qué tal?"
    mock_bd.get_chat.return_value = None
    with pytest.raises(NoChatFound) as exc:
        servicio_chat.continue_conversation(id_conversacion, query=consulta)
    assert str(exc.value) == "Chat not found"  # Cambiado a inglés

def test_falta_entrada(servicio_chat, mock_bd):
    id_conversacion = "456"
    consulta = None
    with pytest.raises(InputNotProvided) as exc:
        servicio_chat.continue_conversation(id_conversacion, query=consulta)
    assert str(exc.value) == "No input provided"  # Cambiado a inglés

def test_continuar_conversacion_con_audio(servicio_chat, mock_bd, mock_agente, mock_transcriptor):
    with patch('app.domain.models.Chat', return_value=MagicMock()) as mock_chat:
        id_conversacion = "456"
        archivo_voz = b"audio"
        mock_chat.return_value.get_conversation_history.return_value = []
        mock_bd.get_chat.return_value = mock_chat.return_value
        mock_agente.get_last_response.return_value = "Hola, cómo estás?"
        mock_transcriptor.transcribe_audio.return_value = "Qué tal?"
        resultado = servicio_chat.continue_conversation(id_conversacion, voice_file=archivo_voz)
        mock_bd.get_chat.assert_called_once_with(id_conversacion)
        mock_transcriptor.transcribe_audio.assert_called_once_with(archivo_voz)
        mock_agente.set_memory_variables.assert_called_once_with([])
        mock_agente.get_last_response.assert_called_once()
        mock_agente.get_conversation_history.assert_called_once()
        mock_bd.save_chat.assert_called_once_with(mock_chat.return_value)
def test_generate_uuid():
    uuid = generate_uuid()
    assert isinstance(uuid, str)
    assert len(uuid) > 0

def test_update_conversation():
    # Arrange
    chat = Chat()
    new_conversation = [human.HumanMessage(content="Hola"), ai.AIMessage(content="Hola, ¿cómo estás?")]

    # Act
    chat.update_conversation(new_conversation)

    # Assert
    assert chat.get_conversation_history() == new_conversation

def test_update_conversation_empty():
    # Arrange
    chat = Chat()
    empty_conversation = []

    # Act
    chat.update_conversation(empty_conversation)

    # Assert
    assert chat.get_conversation_history() == []

def test_get_conversation_history():
    # Arrange
    chat = Chat()

    # Act
    history = chat.get_conversation_history()

    # Assert
    assert isinstance(history, list)
    assert len(history) == 0


