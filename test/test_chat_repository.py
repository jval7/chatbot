from app.adapters.chat_repository import InMemoryChatRepository, DynamoDb
from app.domain.models import Chat
from unittest.mock import Mock, patch


def test_in_memory_chat_repository():
    repo = InMemoryChatRepository()
    chat = Chat(id="123", conversation=[])
    repo.save_chat(chat)
    retrieved_chat = repo.get_chat("123")
    assert retrieved_chat is not None  
    assert retrieved_chat.id == "123"
    assert retrieved_chat.conversation == chat.conversation 

def test_in_memory_chat_repository_non_existent_chat():
    repo = InMemoryChatRepository()
    retrieved_chat = repo.get_chat("non_existent_id")
    assert retrieved_chat is None  

def test_dynamo_db_save_chat():
    mock_table = Mock()
    with patch("app.adapters.chat_repository.boto3.resource") as mock_boto:
        mock_boto.return_value.Table.return_value = mock_table
        repo = DynamoDb(table_name="test_table")
        chat = Chat(id="123", conversation=[])
        repo.save_chat(chat)
        mock_table.put_item.assert_called_once_with(Item=chat.dict())

def test_dynamo_db_get_chat():
    mock_table = Mock()
    mock_table.get_item.return_value = {"Item": {"id": "123", "conversation": []}}
    with patch("app.adapters.chat_repository.boto3.resource") as mock_boto:
        mock_boto.return_value.Table.return_value = mock_table
        repo = DynamoDb(table_name="test_table")
        chat = repo.get_chat("123")
        assert chat is not None
        assert chat.id == "123"


def test_dynamo_db_get_chat_non_existent():
    mock_table = Mock()
    mock_table.get_item.return_value = {} 
    with patch("app.adapters.chat_repository.boto3.resource") as mock_boto:
        mock_boto.return_value.Table.return_value = mock_table
        repo = DynamoDb(table_name="test_table")
        chat = repo.get_chat("non_existent_id")
        assert chat is None 
