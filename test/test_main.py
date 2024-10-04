from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.domain.models import NoChatFound, InputNotProvided

client = TestClient(app)

class MockChatService:

    def start_conversation(self):
        return "mock_chat_id"

    def continue_conversation(self, conversation_id, query=None, voice_file_bytes=None):
        if conversation_id == "non_existent_chat_id":
            raise NoChatFound()
        if query is None and voice_file_bytes is None:
            raise InputNotProvided()
        return "mock_response"

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_start_chat(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    assert response.json() == {"chat_id": "mock_chat_id"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    chat_id = response.json()["chat_id"]
    response = client.post(f"/chats/{chat_id}/continue", json={"query": "Hello"})
    assert response.status_code == 200
    assert response.json() == {"response": "mock_response"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_no_chat_found(mock_service):
    response = client.post("/chats/non_existent_chat_id/continue", json={"query": "Hello"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_no_input_provided(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    chat_id = response.json()["chat_id"]
    response = client.post(f"/chats/{chat_id}/continue", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "No input provided"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_invalid_query(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    chat_id = response.json()["chat_id"]
    response = client.post(f"/chats/{chat_id}/continue", json={"query": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "No input provided"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_with_voice(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    chat_id = response.json()["chat_id"]
    voice_file = ("voice.wav", b"dummy_voice_data")
    response = client.post(f"/chats/{chat_id}/continue-with-voice", files={"voice_file": voice_file})
    assert response.status_code == 200
    assert response.json() == {"response": "mock_response"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_with_voice_no_chat_found(mock_service):
    voice_file = ("voice.wav", b"dummy_voice_data")
    response = client.post("/chats/non_existent_chat_id/continue-with-voice", files={"voice_file": voice_file})
    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

@patch('app.entrypoints.ChatService', new_callable=lambda: MockChatService)
def test_continue_chat_with_voice_no_input_provided(mock_service):
    response = client.post("/chats/")
    assert response.status_code == 200
    chat_id = response.json()["chat_id"]
    response = client.post(f"/chats/{chat_id}/continue-with-voice")
    assert response.status_code == 400
    assert response.json() == {"detail": "No input provided"}
