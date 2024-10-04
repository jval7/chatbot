from unittest.mock import patch, Mock
from app.bootstrap import BootStrap
import pinecone

@patch("app.bootstrap.pinecone.Index")
def test_chat_service_creation(mock_pinecone_index):
    mock_pinecone_index.return_value = Mock()
    bootstrap = BootStrap()
    chat_service = bootstrap.get_chat_service()
    assert chat_service is not None
