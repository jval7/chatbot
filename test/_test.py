import pytest
from app.services.usecases import ChatService, models, InputNotProvided, NoChatFound
from unittest.mock import Mock

@pytest.fixture
def mockedAgentforTesting():
    testingAgent = Mock()
    testingAgent.get_last_response.return_value = "response"
    testingAgent.get_conversation_history.return_value = ["query", "response"]
    return testingAgent

@pytest.fixture
def mockedTranscriberforTesting():
    transcriber = Mock()
    transcriber.transcribe_audio.return_value = "transcribed query"
    return transcriber

@pytest.fixture
def mockedDatabaseforTesting():
    db = Mock()
    db.get_chat.return_value = models.Chat(id="conversation_id")
    return db

@pytest.fixture
def chat_service(mockedAgentforTesting, mockedDatabaseforTesting, mockedTranscriberforTesting):
    return ChatService(agent=mockedAgentforTesting, db=mockedDatabaseforTesting, transcriber=mockedTranscriberforTesting)

def test_should_start_a_normal_conversation(chat_service, mockedDatabaseforTesting):
    mockedDatabaseforTesting.save_chat.return_value = None
    resultNormalConversation = chat_service.start_conversation()

    assert resultNormalConversation is not None
    mockedDatabaseforTesting.save_chat.assert_called_once()

def test_continue_conversation_no_input(chat_service):
    with pytest.raises(InputNotProvided):
        chat_service.continue_conversation(conversation_id="0912838551265")

def test_should_continue_conversation_with_text(chat_service, mockedDatabaseforTesting, mockedAgentforTesting):
    result = chat_service.continue_conversation(conversation_id="44567123981249", query="Describeme un SOC")

    assert result == "response"
    mockedDatabaseforTesting.get_chat.assert_called_once_with("44567123981249")
    mockedAgentforTesting.set_memory_variables.assert_called_once()
    mockedAgentforTesting.assert_called_once_with(query="Describeme un SOC")

def test_trying_to_figure_out_if_a_conversation_can_be_continued_without_a_valid_id(chat_service, mockedDatabaseforTesting):
    mockedDatabaseforTesting.get_chat.return_value = None
    with pytest.raises(NoChatFound):
        chat_service.continue_conversation(conversation_id="12387612386", query="Muy buenos días, ¿cómo puedo ayudarte?")

def test_has_the_ability_to_answer_back_using_voice_over_text_or_similar(chat_service, mockedDatabaseforTesting, mockedAgentforTesting, mockedTranscriberforTesting):
    voice_file = b"voice data"
    result = chat_service.continue_conversation(conversation_id="18746187746372413", voice_file=voice_file)

    assert result == "response"
    mockedTranscriberforTesting.transcribe_audio.assert_called_once_with(voice_file)
    mockedDatabaseforTesting.get_chat.assert_called_once_with("18746187746372413")
    mockedAgentforTesting.set_memory_variables.assert_called_once()
    mockedAgentforTesting.assert_called_once_with(query="transcribed query")

