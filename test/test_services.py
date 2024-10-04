import pytest
from app.services.usecases import ChatService, NoChatFound, InputNotProvided
from unittest.mock import Mock


def test_start_conversation():
    agent_mock = Mock()
    db_mock = Mock()
    transcriber_mock = Mock()
    service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    db_mock.save_chat.return_value = None
    chat_id = service.start_conversation()
    assert chat_id is not None
    db_mock.save_chat.assert_called_once()


def test_continue_conversation_with_query():
    agent_mock = Mock()
    db_mock = Mock()
    transcriber_mock = Mock()
    service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    mock_chat = Mock()
    mock_chat.id = "123" 
    db_mock.get_chat.return_value = mock_chat
    agent_mock.get_last_response.return_value = "Respuesta generada"
    response = service.continue_conversation(conversation_id="123", query="Hola")
    assert response == "Respuesta generada"


def test_continue_conversation_with_no_chat_found():
    agent_mock = Mock()
    db_mock = Mock()
    transcriber_mock = Mock()
    service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    db_mock.get_chat.return_value = None
    with pytest.raises(NoChatFound):
        service.continue_conversation(conversation_id="non_existent_id", query="Hola")


def test_continue_conversation_with_no_query():
    agent_mock = Mock()
    db_mock = Mock()
    transcriber_mock = Mock()
    service = ChatService(agent=agent_mock, db=db_mock, transcriber=transcriber_mock)
    with pytest.raises(InputNotProvided):
        service.continue_conversation(conversation_id="123", query="")
