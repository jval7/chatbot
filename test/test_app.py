import pytest
from app.domain import ports, models
from app.services.usecases import ChatService
from unittest.mock import MagicMock


@pytest.fixture
def mock_agent():
    return MagicMock(spec=ports.AgentPort)


@pytest.fixture
def mock_db():
    return MagicMock(spec=ports.ChatRepository)


@pytest.fixture
def mock_transcriber():
    return MagicMock(spec=ports.TranscriptionPort)


@pytest.fixture
def chat_service(mock_agent, mock_db, mock_transcriber):
    return ChatService(agent=mock_agent, db=mock_db, transcriber=mock_transcriber)



def test_deberia_iniciar_chat_al_llamar_iniciar_chat(chat_service, mock_db):
    # Arrange
    expected_chat_model = models.Chat(id="mock_chat_id")
    mock_db.save_chat.return_value = None
    mock_db.save_chat.side_effect = lambda chat: setattr(chat, 'id', expected_chat_model.id)

    # Act
    chat_id = chat_service.start_conversation()

    # Assert
    mock_db.save_chat.assert_called_once()
    assert chat_id == expected_chat_model.id


def test_deberia_continuar_conversacion_con_consulta_al_llamar_continuar_conversacion(chat_service, mock_db, mock_agent):

    conversation_id = "mock_chat_id"
    query = "¿Por qué Java nunca se siente solo?"

    chat_model = MagicMock(spec=models.Chat)
    chat_model.id = conversation_id
    chat_model.get_conversation_history.return_value = []

    mock_db.get_chat.return_value = chat_model
    mock_agent.get_last_response.return_value = "¡Porque siempre tiene un montón de classes!"


    response = chat_service.continue_conversation(conversation_id, query=query)


    mock_db.get_chat.assert_called_once_with(conversation_id)
    mock_agent.set_memory_variables.assert_called_once_with([])
    mock_agent.assert_called_once_with(query=query)
    assert response == "¡Porque siempre tiene un montón de classes!"


def test_debería_actualizar_chat_al_llamar_a_actualizar_chat(chat_service, mock_db, mock_agent):

    chat_id = "mock_chat_id"

    chat_model = MagicMock(spec=models.Chat)
    chat_model.id = chat_id
    mock_db.get_chat.return_value = chat_model

    mock_agent.get_conversation_history.return_value = ["Hi there!", "I'm doing great, thanks!"]



    chat_service._update_chat(chat_model)


    mock_agent.get_conversation_history.assert_called_once()
    mock_agent.get_conversation_history.return_value = ["Hi there!", "I'm doing great, thanks!"]
    mock_db.save_chat.assert_called_once_with(chat_model)
