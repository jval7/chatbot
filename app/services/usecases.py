from app.domain import ports, models
from app.logs import logger


class ChatService:
    def __init__(
        self,
        agent: ports.AgentPort,
        db: ports.ChatRepository,
        transcriber: ports.TranscriptionPort,
    ) -> None:
        self._agent = agent
        self._db = db
        self._transcriber = transcriber

    def start_conversation(self) -> str:
        chat_model = models.Chat()
        logger.info("Saving chat")
        self._db.save_chat(chat_model)
        logger.info("Chat saved")
        return chat_model.id

    def continue_conversation(
        self,
        conversation_id: str,
        query: str | None = None,
        voice_file: bytes | None = None,
    ) -> str:
        if voice_file:
            query = self._transcriber.transcribe_audio(voice_file)
        elif query:
            query = query
        else:
            raise InputNotProvided("No input provided")

        chat = self._db.get_chat(conversation_id)
        if chat is None:
            raise NoChatFound("Chat not found")
        self._agent.set_memory_variables(chat.get_conversation_history())
        self._agent(query=query)
        self._update_chat(chat)
        return self._agent.get_last_response()

    def _update_chat(self, chat: models.Chat) -> None:
        chat = models.Chat(id=chat.id)
        chat.update_conversation(self._agent.get_conversation_history())
        self._db.save_chat(chat)


class NoChatFound(Exception):
    pass


class InputNotProvided(Exception):
    pass
