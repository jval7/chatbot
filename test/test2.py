# test_usecases.py ubicado en tests/services

import pytest
from unittest.mock import Mock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain import models


def test_update_chat():
    # Crear un mock para el agente
    mock_agent = Mock()
    conversation_history = [
        {"type": "human", "content": "Hola"},
        {"type": "ai", "content": "Hola, ¿en qué puedo ayudarte?"}
    ]
    mock_agent.get_conversation_history.return_value = conversation_history

    # Crear un mock para el repositorio de chats
    mock_db = Mock()

    # Crear un mock para el transcriptor (aunque no se utiliza en esta prueba)
    mock_transcriber = Mock()

    # Instanciar ChatService con los mocks
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Crear un objeto Chat de prueba
    chat = models.Chat(id="test_chat_id")

    # Llamar al método _update_chat
    chat_service._update_chat(chat)

    # Verificar que get_conversation_history fue llamado
    mock_agent.get_conversation_history.assert_called_once()

    # Verificar que save_chat fue llamado con el chat actualizado
    expected_chat = models.Chat(id="test_chat_id")
    expected_chat.update_conversation(conversation_history)

    # Obtener el chat que fue pasado a save_chat
    saved_chat = mock_db.save_chat.call_args[0][0]

    # Assert para comprobar que el ID coincide
    assert saved_chat.id == expected_chat.id
    # Assert para comprobar que la conversación fue actualizada correctamente
    assert saved_chat.conversation.history == expected_chat.conversation.history





def test_continue_conversation_with_query():
    # Mocks de dependencias
    mock_agent = Mock()
    mock_agent.get_last_response.return_value = "Respuesta del agente"
    mock_db = Mock()
    mock_transcriber = Mock()

    # Simular que el chat existe en la base de datos
    chat = models.Chat(id="test_chat_id")
    mock_db.get_chat.return_value = chat

    # Instanciar el servicio
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Ejecutar el método con un query
    response = chat_service.continue_conversation(
        conversation_id="test_chat_id",
        query="Hola",
        voice_file=None
    )

    # Verificaciones
    mock_db.get_chat.assert_called_once_with("test_chat_id")
    mock_agent.set_memory_variables.assert_called_once_with(chat.get_conversation_history())
    mock_agent.assert_called_once_with(query="Hola")
    mock_db.save_chat.assert_called_once()
    assert response == "Respuesta del agente"


def test_continue_conversation_with_voice_file():
    # Mocks de dependencias
    mock_agent = Mock()
    mock_agent.get_last_response.return_value = "Respuesta del agente"
    mock_db = Mock()
    mock_transcriber = Mock()
    mock_transcriber.transcribe_audio.return_value = "Texto transcrito"

    # Simular que el chat existe en la base de datos
    chat = models.Chat(id="test_chat_id")
    mock_db.get_chat.return_value = chat

    # Instanciar el servicio
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Ejecutar el método con un voice_file
    response = chat_service.continue_conversation(
        conversation_id="test_chat_id",
        query=None,
        voice_file=b"archivo de audio"
    )

    # Verificaciones
    mock_transcriber.transcribe_audio.assert_called_once_with(b"archivo de audio")
    mock_db.get_chat.assert_called_once_with("test_chat_id")
    mock_agent.set_memory_variables.assert_called_once_with(chat.get_conversation_history())
    mock_agent.assert_called_once_with(query="Texto transcrito")
    mock_db.save_chat.assert_called_once()
    assert response == "Respuesta del agente"


def test_continue_conversation_no_input():
    # Mocks de dependencias
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    # Instanciar el servicio
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Ejecutar el método sin query ni voice_file y verificar que lanza excepción
    with pytest.raises(InputNotProvided) as exc_info:
        chat_service.continue_conversation(
            conversation_id="test_chat_id",
            query=None,
            voice_file=None
        )

    assert str(exc_info.value) == "No input provided"


def test_continue_conversation_chat_not_found():
    # Mocks de dependencias
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    # Simular que el chat no existe en la base de datos
    mock_db.get_chat.return_value = None

    # Instanciar el servicio
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Ejecutar el método y verificar que lanza excepción
    with pytest.raises(NoChatFound) as exc_info:
        chat_service.continue_conversation(
            conversation_id="non_existent_chat_id",
            query="Hola",
            voice_file=None
        )

    assert str(exc_info.value) == "Chat not found"


# test_usecases.py ubicado en tests/services
import pytest
from unittest.mock import Mock, patch
from app.services.usecases import ChatService
from app.domain import models


def test_start_conversation():
    # Mocks de dependencias
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()

    # Instanciar el servicio
    chat_service = ChatService(
        agent=mock_agent,
        db=mock_db,
        transcriber=mock_transcriber
    )

    # Parchar el logger para evitar logs durante la prueba
    with patch('app.services.usecases.logger') as mock_logger:
        # Ejecutar el método
        chat_id = chat_service.start_conversation()

        # Verificaciones
        # Verificar que save_chat fue llamado una vez
        mock_db.save_chat.assert_called_once()

        # Obtener el chat que fue pasado a save_chat
        saved_chat = mock_db.save_chat.call_args[0][0]

        # Verificar que se creó un objeto Chat
        assert isinstance(saved_chat, models.Chat)

        # Verificar que el ID retornado coincide con el ID del chat guardado
        assert chat_id == saved_chat.id

        # Verificar que se llamaron los logs correspondientes
        mock_logger.info.assert_any_call("Saving chat")
        mock_logger.info.assert_any_call("Chat saved")
        assert mock_logger.info.call_count == 2
