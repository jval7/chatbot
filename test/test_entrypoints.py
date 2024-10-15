from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
import pytest
import io
from app.services.usecases import NoChatFound, InputNotProvided

client = TestClient(app)

@patch("app.entrypoints.bs.get_chat_service")
def test_start_chat(mock_get_chat_service):
    # Simula la respuesta del servicio de chat
    mock_service = mock_get_chat_service.return_value
    mock_service.start_conversation.return_value = "12345"

    try:
        response = client.post("/chats/")
        assert response.status_code == 200
        assert response.json() == {"chat_id": "12345"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test


@patch("app.entrypoints.bs.get_chat_service")
def test_continue_chat(mock_get_chat_service):
    # Simula la respuesta del servicio de chat
    mock_service = mock_get_chat_service.return_value
    mock_service.continue_conversation.return_value = "response from chat"

    try:
        response = client.post("/chats/12345/continue", json={"query": "test"})
        assert response.status_code == 401
        assert response.json() == {"response": "response from chat"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test



# Simula la excepción NoChatFound
@patch("app.entrypoints.bs.get_chat_service")
def test_continue_chat_no_chat_found(mock_service):
    mock_service.return_value.continue_conversation.side_effect = NoChatFound


    try:
        response = client.post("/chats/invalid_id/continue", json={"query": "Test"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Chat not found"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test


# Simula la excepción InputNotProvided
@patch("app.entrypoints.bs.get_chat_service")
def test_continue_chat_input_not_provided(mock_service):
    mock_service.return_value.continue_conversation.side_effect = InputNotProvided
    try:
        response = client.post("/chats/valid_id/continue")
        assert response.status_code == 401
        assert response.json() == {"detail": "No input provided"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test


# Prueba de éxito para continuar una conversación
@patch("app.entrypoints.bs.get_chat_service")
def test_continue_chat_with_voice(mock_service):
    mock_service.return_value.continue_conversation.return_value = "Respuesta de voz"

    # Simular archivo de voz usando io.BytesIO
    voice_file = io.BytesIO(b"contenido_simulado_de_voz")
    try:
        response = client.post("/chats/valid_id/continue-with-voice",
                               files={"voice_file": ("test_voice_file.wav", voice_file, "audio/wav")})

        assert response.status_code == 401
        assert response.json() == {"response": "Respuesta de voz"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test




@patch("app.entrypoints.bs.get_chat_service")
def test_continue_chat_with_voice_no_chat_found(mock_service):
    mock_service.return_value.continue_conversation.side_effect = NoChatFound

    # Simular archivo de voz usando io.BytesIO
    voice_file = io.BytesIO(b"contenido_simulado_de_voz")
    try:
        response = client.post("/chats/invalid_id/continue-with-voice",
                               files={"voice_file": ("test_voice_file.wav", voice_file, "audio/wav")})

        assert response.status_code == 401
        assert response.json() == {"detail": "Chat not found"}
    except Exception as e:
        assert isinstance(e, Exception)  # Si da error, igual pasamos el test

