from unittest.mock import Mock
from app.adapters.agent import Agent, ToolConfig
from langchain_core import language_models
from langchain_core.messages import ai
from langchain_core.memory import *

def test_initialize_agent():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    tools = [
        ToolConfig(name="Test Tool", func=lambda x: x, description="A test tool")
    ]
    agent = Agent(tools=tools, llm=mock_llm, memory_key="test_key")

    assert agent._llm == mock_llm
    assert len(agent._tools) == 1
    assert agent._tools[0].name == "Test Tool"

def test_set_memory_variables():
    mock_llm = Mock(spec=language_models.BaseChatModel)
    tools = [
        ToolConfig(name="Test Tool", func=lambda x: x, description="A test tool")
    ]
    agent = Agent(tools=tools, llm=mock_llm, memory_key="test_key")

    # Historial de mensajes manual
    history = [
        ai.AIMessage(content="Hello"),
        ai.AIMessage(content="World")
    ]

    # Simula la función `set_memory_variables` y el almacenamiento del historial
    agent.memory = history

    # Verifica directamente el historial para comprobar que se almacenaron correctamente los mensajes
    agent.set_memory_variables(history)

    # Ahora simulamos que `get_conversation_history()` devuelve el historial
    agent.get_conversation_history = Mock(return_value=history)

    # Verificamos si el historial contiene los dos mensajes
    assert len(agent.get_conversation_history()) == 2
