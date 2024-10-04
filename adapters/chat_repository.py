from app.domain import models
from app.domain import ports
import boto3


class InMemoryChatRepository(ports.ChatRepository):
    def __init__(self) -> None:
        self._db: dict[str, dict[str, models.Chat]] = {}

    def save_chat(self, chat: models.Chat) -> None:
        if not chat.id:
            raise
        self._db[chat.id] = chat.dict()

    def get_chat(self, chat_id: str) -> models.Chat | None:
        chat = self._db.get(chat_id)
        if chat is None:
            return None
        return models.Chat(id=chat_id, conversation=chat["conversation"])


class DynamoDb(ports.ChatRepository):
    def __init__(self, table_name: str) -> None:
        self._client = boto3.resource("dynamodb", region_name="us-east-1")
        self._table = self._client.Table(table_name)

    def save_chat(self, chat: models.Chat) -> None:
        self._table.put_item(Item=chat.dict())

    def get_chat(self, chat_id: str) -> models.Chat | None:
        response = self._table.get_item(Key={"id": chat_id})
        if "Item" not in response:
            return None
        return models.Chat(id=chat_id, conversation=response["Item"]["conversation"])
