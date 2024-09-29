from typing import List, Any, Callable, cast

import pydantic
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.chains.conversation import memory
from langchain_core import language_models
from langchain_core.messages import ai

from app.domain.ports import AgentPort


class ToolConfig(pydantic.BaseModel):
    name: str
    func: Callable
    description: str


class Agent(AgentPort):
    def __init__(
        self,
        tools: List[ToolConfig],
        llm: language_models.BaseChatModel,
        memory_key: str,
    ) -> None:
        self._memory = memory.ConversationBufferWindowMemory(
            memory_key=memory_key,
            return_messages=True,
            k=5,
        )
        self._tools: List[Tool] = [
            Tool(name=tool.name, func=tool.func, description=tool.description)
            for tool in tools
        ]
        self._llm = llm
        self._agent = initialize_agent(
            agent="chat-conversational-react-description",
            tools=self._tools,
            llm=self._llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            memory=self._memory,
        )

    def __call__(self, query: str) -> dict[str, Any]:
        return cast(dict[str, Any], self._agent(query))

    def get_conversation_history(self) -> list[ai.BaseMessage]:
        conversations = self._memory.load_memory_variables({})
        if "chat_history" not in conversations:
            return []
        return cast(list[ai.BaseMessage], conversations["chat_history"])

    def set_memory_variables(self, history: list[ai.BaseMessage]) -> None:
        self._memory.chat_memory.messages = history

    def get_last_response(self) -> str:
        return cast(str, self._memory.chat_memory.messages[-1].content)
