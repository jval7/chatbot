from typing import cast, List
import shortuuid
from langchain_core.messages import human, ai
from pydantic import v1 as pd1

def generate_uuid() -> str:
    return cast(str, shortuuid.uuid())

class Conversation(pd1.BaseModel):
    history: List[ai.AIMessage | human.HumanMessage] = pd1.Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

class Chat(pd1.BaseModel):
    id: str = pd1.Field(default_factory=generate_uuid)
    conversation: Conversation = pd1.Field(default_factory=Conversation)

    class Config:
        arbitrary_types_allowed = True

    def update_conversation(self, current_conversation: List[ai.BaseMessage]) -> None:
        self.conversation.history = current_conversation

    def get_conversation_history(self) -> List[ai.BaseMessage]:
        return self.conversation.history