from langchain import chat_models

from app import adapters
from app import configurations
from app.domain import ports
from app.services import usecases
from app.logs import logger


class BootStrap:
    def __init__(
        self,
        agent: ports.AgentPort | None = None,
        db: ports.ChatRepository | None = None,
        transcriber: ports.TranscriptionPort | None = None,
    ) -> None:
        self._agent = agent
        self._db = db
        self._chat_service: usecases.ChatService | None = None
        self._transcriber = transcriber
        logger.info("BootStrap initialized")

    def get_chat_service(self) -> usecases.ChatService | None:
        if self._chat_service:
            logger.info("Returning existing chat service")
            return self._chat_service
        if not self._db:
            logger.info("Creating DynamoDb instance")
            self._db = adapters.DynamoDb(table_name=configurations.configs.table_name)
        if not self._agent:
            logger.info("Creating ChatOpenAI instance")
            llm = chat_models.ChatOpenAI(
                openai_api_key=configurations.configs.openai_api_key,
                model_name=configurations.configs.openai_model_name,
                temperature=configurations.configs.temperature,
            )
            logger.info("Creating RetrievalQa instance")
            retriever = adapters.RetrievalQa(
                llm=llm,
                index_name=configurations.configs.index_name,
                embedding_model_name=configurations.configs.embedding_model_name,
                openai_api_key=configurations.configs.openai_api_key,
                text_key=configurations.configs.text_key,
                pinecone_api_key=configurations.configs.pinecone_api_key,
            ).get_chain()
            tools = [
                adapters.ToolConfig(
                    name="Knowledge Base",
                    func=retriever.run,
                    description=(
                        "use this tool when answering general knowledge queries to get "
                        "more information about the topic"
                    ),
                )
            ]
            self._agent = adapters.Agent(
                tools=tools, llm=llm, memory_key="chat_history"
            )

        if not self._transcriber:
            logger.info("Creating OpenAITranscriptionClient instance")
            self._transcriber = adapters.OpenAITranscriptionClient(
                api_key=configurations.configs.openai_api_key,
                api_url=configurations.configs.openai_transcription_url,
                transcription_model=configurations.configs.transcription_model,
            )
        self._chat_service = usecases.ChatService(
            agent=self._agent, db=self._db, transcriber=self._transcriber
        )
        logger.info("Chat service created")
        return self._chat_service
