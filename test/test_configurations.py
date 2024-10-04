from unittest import mock
import pytest
from app.configurations import Configs

@mock.patch.dict("os.environ", {
    "OPENAI_API_KEY": "test_key",
    "OPENAI_MODEL_NAME": "test_model",
    "TEMPERATURE": "0.7",
    "OPENAI_TRANSCRIPTION_URL": "test_url",
    "TRANSCRIPTION_MODEL": "test_model",
    "INDEX_NAME": "test_index",
    "TEXT_KEY": "test_key",
    "EMBEDDING_MODEL_NAME": "test_embedding_model",
    "PINECONE_API_KEY": "test_pinecone_key",
    "TABLE_NAME": "test_table",
    "LANGFUSE_SECRET_KEY": "test_secret_key",
    "LANGFUSE_PB_KEY": "test_pb_key",
    "LANGFUSE_HOST": "test_host"
})
def test_configs_load():
    configs = Configs()
    assert configs.openai_api_key == "test_key"
