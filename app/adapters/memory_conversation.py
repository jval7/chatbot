# from langchain.chains.conversation import memory
# from langchain.memory import chat_memory
#
# from langchain_core.messages import ai
#
#
# class Memory:
#     def __init__(self, memory_key: str) -> None:
#         self._memory = memory.ConversationBufferMemory(
#             memory_key=memory_key, return_messages=True
#         )
#
#     def get_memory(self) -> chat_memory.BaseChatMemory:
#         return self._memory
#
#     def get_conversation_history(self) -> list[ai.BaseMessage]:
#         return self._memory.load_memory_variables({})["chat_history"]
#
#     def set_memory_variables(self, history: list[ai.BaseMessage]) -> None:
#         self._memory.chat_memory.messages = history
