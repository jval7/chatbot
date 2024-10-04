import pydantic_settings


class Configs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    # openai
    openai_api_key: str
    openai_model_name: str
    temperature: float
    openai_transcription_url: str
    transcription_model: str
    # pinecone
    index_name: str
    text_key: str
    embedding_model_name: str
    pinecone_api_key: str
    # dynamodb
    table_name: str
    # langfuse
    langfuse_secret_key: str
    langfuse_pb_key: str
    langfuse_host: str


configs = Configs()
