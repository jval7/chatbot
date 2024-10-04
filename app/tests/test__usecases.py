

from unittest.mock import Mock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain.models import Chat, Conversation
from app.domain.ports import ChatRepository, AgentPort, TranscriptionPort
from langchain_core.messages import ai
import pytest


def test_start_conversation():
 
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    
    chat_id = chat_service.start_conversation()

    
    assert isinstance(chat_id, str)
    mock_db.save_chat.assert_called_once()  


def test_update_conversation():
    
    chat = Chat()
    new_messages = [ai.AIMessage(content="menssage")]

  
    chat.update_conversation(new_messages)


    assert chat.get_conversation_history() == new_messages


def test_get_conversation_history():
  
    chat = Chat()
    expected_history = [ai.AIMessage(content="funciona")]

   
    chat.update_conversation(expected_history)
    history = chat.get_conversation_history()

    
    assert history == expected_history


def test_continue_conversation_with_audio():
   
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_id = "test_chat_id"
    voice_file = b"audio_data"

    
    mock_chat = Mock()
    mock_chat.get_conversation_history.return_value = []
    mock_chat.id = chat_id  
    mock_db.get_chat.return_value = mock_chat

    
    mock_transcriber.transcribe_audio.return_value = "text"
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    # Execution
    response = chat_service.continue_conversation(conversation_id=chat_id, voice_file=voice_file)

    # Assert
    mock_transcriber.transcribe_audio.assert_called_once_with(voice_file)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query="Transcribed text")
    mock_db.save_chat.assert_called_once()
    assert response is not None  


def test_continue_conversation_no_chat_found():
    # Configuration
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)

    mock_db.get_chat.return_value = None  


    with pytest.raises(NoChatFound):
        chat_service.continue_conversation("non_existent")


def test_continue_conversation_with_query():
  
    mock_agent = Mock()
    mock_db = Mock()
    mock_transcriber = Mock()
    chat_service = ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)


    chat_id = "test_chat_id"
    mock_chat = Mock()
    mock_chat.get_conversation_history.return_value = []
    mock_chat.id = chat_id  # Asegúrate de que el id sea una cadena
    mock_db.get_chat.return_value = mock_chat
    query = "Hello!"

    # Execution
    response = chat_service.continue_conversation(conversation_id=chat_id, query=query)

    # Assert
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    mock_db.save_chat.assert_called_once()
    assert response is not None  



class TestChatRepository:
    def test_save_chat(self):
       
        mock_repository = Mock(ChatRepository)
        mock_chat = Mock(spec=Chat)

        
        mock_repository.save_chat(mock_chat)

    
        mock_repository.save_chat.assert_called_once_with(mock_chat)

    def test_get_chat(self):
       
        mock_repository = Mock(ChatRepository)
        mock_chat = Mock(spec=Chat)
        mock_repository.get_chat.return_value = mock_chat

        
        chat = mock_repository.get_chat("chat_id_123")

     
        assert chat == mock_chat
        mock_repository.get_chat.assert_called_once_with("chat_id_123")

    def test_get_chat_none(self):
        
        mock_repository = Mock(ChatRepository)
        mock_repository.get_chat.return_value = None

        
        chat = mock_repository.get_chat("non_existent_chat_id")

       
        assert chat is None
        mock_repository.get_chat.assert_called_once_with("non_existent_chat_id")


class TestAgentPort:
    def test_set_memory_variables(self):
       
        mock_agent = Mock(AgentPort)
        history = [ai.BaseMessage(type="user", content="Hello"), ai.BaseMessage(type="user", content="Hi!")]

       
        mock_agent.set_memory_variables(history)

        
        mock_agent.set_memory_variables.assert_called_once_with(history)

    def test_agent_call(self):
       
        mock_agent = Mock(AgentPort)

        
        mock_agent.side_effect = lambda query: {"response": "Hello, how can I help you?"}

       
        response = mock_agent("Hello")

       
        assert response == {"response": "Hello, how can I help you?"}
        mock_agent.assert_called_once_with("Hello")

    def test_get_conversation_history(self):
        
        mock_agent = Mock(AgentPort)
        history = [ai.BaseMessage(type="user", content="Hello"), ai.BaseMessage(type="user", content="Hi!")]
        mock_agent.get_conversation_history.return_value = history

        
        retrieved_history = mock_agent.get_conversation_history()

        
        assert retrieved_history == history
        mock_agent.get_conversation_history.assert_called_once()

    def test_get_last_response(self):
       
        mock_agent = Mock(AgentPort)
        mock_agent.get_last_response.return_value = "Goodbye!"

        
        response = mock_agent.get_last_response()

        
        assert response == "Goodbye!"
        mock_agent.get_last_response.assert_called_once()

