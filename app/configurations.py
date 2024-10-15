from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    openai_api_key: str = "default_openai_api_key"
    openai_model_name: str = "text-davinci-003"
    temperature: float = 0.7
    openai_transcription_url: str = "https://api.openai.com/v1/audio/transcriptions"
    transcription_model: str = "whisper-1"
    index_name: str = "default_index"
    text_key: str = "text"
    embedding_model_name: str = "text-embedding-ada-002"
    pinecone_api_key: str = "default_pinecone_api_key"
    langfuse_secret_key: str = "default_langfuse_secret_key"
    langfuse_pb_key: str = "default_langfuse_pb_key"
    langfuse_host: str = "https://default-langfuse-host.com"

    # Agregar el atributo table_name
    table_name: str = "nombre_de_tu_tabla"  # Aquí defines el nombre de la tabla


# Crear la instancia de configuración
configs = Configs()
