from unittest.mock import MagicMock
import pytest
from app.services.usecases import ChatService, NoChatFound, InputNotProvided


def test_iniciar_conversacion():
    # Mock de las dependencias
    mock_agent = MagicMock()
    mock_db = MagicMock()
    mock_transcriber = MagicMock()

    # Instanciar ChatService con los mocks
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Llamar al método que queremos probar
    chat_id = chat_service.start_conversation()

    # Verificaciones
    assert mock_db.save_chat.call_count == 1  # Verificar que se guardó el chat exactamente una vez
    assert isinstance(chat_id, str)  # Verificar que el chat_id es un string


def test_continuar_conversacion_con_texto():
    # Mock de las dependencias
    mock_agent = MagicMock()
    mock_db = MagicMock()
    mock_transcriber = MagicMock()

    # Crear un chat mockeado con un ID válido
    mock_chat = MagicMock()
    mock_chat.id = "12345"  # Definir un ID de tipo str válido
    mock_db.get_chat.return_value = mock_chat

    # Instanciar ChatService
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Definir el comportamiento del agente
    mock_agent.get_last_response.return_value = "respuesta_esperada"

    # Llamar al método que queremos probar
    response = chat_service.continue_conversation(conversation_id="123", query="Hola")

    # Verificaciones
    mock_db.get_chat.assert_called_with("123")  # Verificar que se buscó el chat correcto
    mock_agent.set_memory_variables.assert_called_once_with(mock_chat.get_conversation_history())  # Verificar que se establecieron variables de memoria
    mock_agent.assert_called_with(query="Hola")  # Verificar que el agente recibió el query
    assert response == "respuesta_esperada"  # Verificar que la respuesta es la correcta

def test_continuar_conversacion_con_archivo_de_voz():
    # Mock de las dependencias
    mock_agent = MagicMock()
    mock_db = MagicMock()
    mock_transcriber = MagicMock()

    # Simular transcripción
    mock_transcriber.transcribe_audio.return_value = "Transcripción del audio"
    mock_chat = MagicMock()
    mock_chat.id = "12345"  # Definir un ID de tipo str válido
    mock_db.get_chat.return_value = mock_chat

    # Instanciar ChatService
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Definir el comportamiento del agente
    mock_agent.get_last_response.return_value = "respuesta_esperada"

    # Llamar al método que queremos probar con un archivo de voz
    voice_file = b"audio_bytes"
    response = chat_service.continue_conversation(conversation_id="123", voice_file=voice_file)

    # Verificaciones
    mock_transcriber.transcribe_audio.assert_called_with(voice_file)  # Verificar que se transcribió el archivo
    mock_agent.assert_called_with(query="Transcripción del audio")  # Verificar que se pasó la transcripción al agente
    assert response == "respuesta_esperada"  # Verificar que la respuesta es la correcta

def test_continuar_conversacion_chat_no_encontrado():
    # Mock de las dependencias
    mock_agent = MagicMock()
    mock_db = MagicMock()
    mock_transcriber = MagicMock()

    # Simular que no se encuentra el chat
    mock_db.get_chat.return_value = None

    # Instanciar ChatService
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Verificar que se lanza la excepción NoChatFound
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="123", query="Hola")


def test_continuar_conversacion_entrada_no_proporcionada():
    # Mock de las dependencias
    mock_agent = MagicMock()
    mock_db = MagicMock()
    mock_transcriber = MagicMock()

    # Instanciar ChatService
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Verificar que se lanza la excepción InputNotProvided cuando no se pasa ni query ni voice_file
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="123")


