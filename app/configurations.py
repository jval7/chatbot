import pydantic_settings


class Configs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    # openai
    openai_api_key: str = "default_key"
    openai_model_name: str = "default_model"
    temperature: float = 0.7
    openai_transcription_url: str = "default_url"
    transcription_model: str = "default_model"
    # pinecone
    index_name: str = "default_index"
    text_key: str = "default_text_key"
    embedding_model_name: str = "default_embedding_model"
    pinecone_api_key: str = "default_pinecone_key"
    # dynamodb
    table_name: str = "default_table"
    # langfuse
    langfuse_secret_key: str = "default_secret_key"
    langfuse_pb_key: str = "default_pb_key"
    langfuse_host: str = "default_host"


configs = Configs()
