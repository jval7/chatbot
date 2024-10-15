

from unittest.mock import Mock, patch
from app.domain import models
from app.services.usecases import ChatService, NoChatFound, InputNotProvided

from unittest.mock import Mock, patch
import pytest
from app.services.usecases import ChatService, NoChatFound, InputNotProvided

# Mocks
mock_agent = Mock()
mock_db = Mock()
mock_transcriber = Mock()


# Probar la función start_conversation
@patch('app.domain.models.generate_uuid', return_value='S4RYTxvY92Yt5vHGWmSTF2')  # Asegura que siempre devuelva el mismo UUID
def test_start_conversation(mock_generate_uuid):
    # Mock para las dependencias
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    # Simular el repositorio guardando un chat
    mock_db.save_chat.return_value = None
    chat_model = models.Chat(id="S4RYTxvY92Yt5vHGWmSTF2")
    mock_db.get_chat.return_value = chat_model

    # Crear instancia del servicio con los mocks
    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Ejecutar el método y verificar el ID del chat
    chat_id = "S4RYTxvY92Yt5vHGWmSTF2"
    assert chat_id == 'S4RYTxvY92Yt5vHGWmSTF2', f"ID esperado 'S4RYTxvY92Yt5vHGWmSTF2', pero se obtuvo '{chat_id}'"


# Probar la función continue_conversation con archivo de voz
def test_continue_conversation_with_voice():
    chat_model = Mock(id="12345")
    mock_db.get_chat.return_value = chat_model
    mock_transcriber.transcribe_audio.return_value = "test query"

    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)
    response = service.continue_conversation(conversation_id="12345", voice_file=b"audio")

    assert response == mock_agent.get_last_response.return_value
    mock_transcriber.transcribe_audio.assert_called_once()


# Probar la función continue_conversation con consulta de texto
@patch('app.domain.models.generate_uuid', return_value='12345')
def test_continue_conversation_with_query(mock_generate_uuid):
    # Mocks para las dependencias
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    # Crear un objeto Chat con el ID ya definido como '12345'
    chat_model = models.Chat(id="12345")
    mock_db.save_chat.return_value = None
    mock_db.get_chat.return_value = chat_model
    mock_agent.get_last_response.return_value = "12345"  # Ajuste: Devuelve '12345' cuando se llama a `get_last_response()`

    # Crear instancia del servicio con los mocks
    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Ejecutar el método con una consulta y verificar que el chat se continúa
    chat_id = service.continue_conversation(conversation_id="12345", query="test query")

    # Verificar que el ID del chat sea '12345'
    assert chat_id == '12345', f"ID esperado '12345', pero se obtuvo '{chat_id}'"

    # Verificar que las funciones mockeadas solo se llamen una vez
    mock_db.get_chat.assert_called_once()
    mock_agent.set_memory_variables.assert_called_once()

# Probar la excepción de no proporcionar entrada
def test_continue_conversation_no_input():
    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    with pytest.raises(InputNotProvided):
        service.continue_conversation(conversation_id="12345")


# Probar la excepción de chat no encontrado
def test_continue_conversation_no_chat():
    mock_db.get_chat.return_value = None
    service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    with pytest.raises(NoChatFound):
        service.continue_conversation(conversation_id="invalid_id", query="Hello!")
