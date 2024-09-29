from typing import cast

import shortuuid
from langchain_core.messages import human, ai
from pydantic import v1 as pd1


def generate_uuid() -> str:
    return cast(str, shortuuid.uuid())


# Entities


class Conversation(pd1.BaseModel):
    history: list[ai.AIMessage | human.HumanMessage] = pd1.Field(default_factory=list)


# Aggregates
class Chat(pd1.BaseModel):
    id: str = pd1.Field(default_factory=generate_uuid)
    conversation: Conversation = pd1.Field(default_factory=Conversation)

    def update_conversation(self, current_conversation: list[ai.BaseMessage]) -> None:
        self.conversation.history = current_conversation

    def get_conversation_history(self) -> list[ai.BaseMessage]:
        return self.conversation.history
