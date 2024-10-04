from unittest.mock import Mock, patch
from langchain import chains
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core import language_models
from pinecone import Pinecone as PineconeClient
from app.adapters.retriever import RetrievalQa


def test_retrieval_qa_initialization():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    with patch("app.adapters.retriever.PineconeClient") as mock_pinecone:
        mock_pinecone_instance = mock_pinecone.return_value
        mock_index = mock_pinecone_instance.Index.return_value
        retrieval_qa = RetrievalQa(
            llm=mock_llm,
            index_name="test_index",
            embedding_model_name="text-embedding-model",
            openai_api_key="test_key",
            text_key="text",
            pinecone_api_key="pinecone_key"
        )
        assert retrieval_qa._llm == mock_llm
        assert retrieval_qa._vectordb._index == mock_index


def test_retrieval_qa_get_chain():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    with patch("app.adapters.retriever.PineconeClient") as mock_pinecone, \
         patch("app.adapters.retriever.OpenAIEmbeddings") as mock_embeddings:
        mock_pinecone_instance = mock_pinecone.return_value
        mock_index = mock_pinecone_instance.Index.return_value
        mock_embedding_instance = mock_embeddings.return_value
        retrieval_qa = RetrievalQa(
            llm=mock_llm,
            index_name="test_index",
            embedding_model_name="text-embedding-model",
            openai_api_key="test_key",
            text_key="text",
            pinecone_api_key="pinecone_key"
        )
        qa_chain = retrieval_qa.get_chain()
        assert isinstance(qa_chain, chains.RetrievalQA)

        # Cambiar 
from unittest.mock import Mock, patch, MagicMock
from langchain import chains
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core import language_models
from app.adapters.retriever import RetrievalQa


def test_retrieval_qa_initialization():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    with patch("app.adapters.retriever.PineconeClient") as mock_pinecone:
        mock_pinecone_instance = MagicMock() 
        mock_pinecone.return_value = mock_pinecone_instance
        retrieval_qa = RetrievalQa(
            llm=mock_llm,
            index_name="test_index",
            embedding_model_name="text-embedding-model",
            openai_api_key="test_key",
            text_key="text",
            pinecone_api_key="pinecone_key"
        )
        assert retrieval_qa._llm == mock_llm


def test_retrieval_qa_get_chain():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    with patch("app.adapters.retriever.PineconeClient") as mock_pinecone, \
         patch("app.adapters.retriever.OpenAIEmbeddings") as mock_embeddings:
        mock_pinecone_instance = MagicMock()
        mock_pinecone.return_value = mock_pinecone_instance
        retrieval_qa = RetrievalQa(
            llm=mock_llm,
            index_name="test_index",
            embedding_model_name="text-embedding-model",
            openai_api_key="test_key",
            text_key="text",
            pinecone_api_key="pinecone_key"
        )
        qa_chain = retrieval_qa.get_chain()
        assert isinstance(qa_chain, chains.RetrievalQA)
