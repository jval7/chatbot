from unittest.mock import Mock
from app.adapters.agent import Agent, ToolConfig
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ai # IS2 Luis Felipe Villota Escobar Grupo 1


def test_agent_initialization():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")
    assert isinstance(agent, Agent)
    assert len(agent._tools) == 1


def test_agent_call():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    mock_llm.return_value = [{"role": "assistant", "content": "Response to Test query"}]
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")
    result = agent({"input": "Test query", "chat_history": []})
    assert isinstance(result, dict)
    assert result['output'] == "Response to Test query"


def test_agent_call_with_invalid_input():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    mock_llm.return_value = [{"role": "assistant", "content": "Invalid input response"}]
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")
    result = agent({"input": "", "chat_history": []})
    assert isinstance(result, dict)
    assert "error" in result

def test_agent_get_conversation_history():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")

    history = agent.get_conversation_history()
    assert isinstance(history, list)


def test_agent_set_memory_variables():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")
    ai_message = ai.AIMessage(content="Test message")
    agent.set_memory_variables([ai_message])
    history = agent.get_conversation_history()
    assert len(history) == 1
    assert history[0].content == "Test message"

def test_agent_get_last_response():
    tool = ToolConfig(name="Test Tool", func=lambda x: x, description="Test tool")
    mock_llm = Mock(spec=BaseChatModel)
    agent = Agent(tools=[tool], llm=mock_llm, memory_key="test_key")

    agent.set_memory_variables([ai.AIMessage(content="Test message")])
    last_response = agent.get_last_response()
    assert last_response == "Test message"
