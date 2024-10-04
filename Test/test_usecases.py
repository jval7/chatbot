import pytest
from unittest.mock import MagicMock
from app.services.usecases import ChatService, InputNotProvided, NoChatFound
from app.domain.models import Chat, Conversation
from app.domain.ports import ChatRepository, AgentPort, TranscriptionPort
from langchain_core.messages import ai
import pytest


def test_iniciar_conversacion():
    # Configuración
    agente_mock = MagicMock()
    base_datos_mock = MagicMock()
    transcriptor_mock = MagicMock()
    servicio_chat = ChatService(agent=agente_mock, db=base_datos_mock, transcriber=transcriptor_mock)

    # Ejecución
    id_conversacion = servicio_chat.start_conversation()

    # Afirmaciones
    assert isinstance(id_conversacion, str)
    base_datos_mock.save_chat.assert_called_once()


def test_actualizar_historial_conversacion():
    # Configuración
    chat_instancia = Chat()
    mensajes = [ai.AIMessage(content="Mensaje de prueba")]

    # Ejecución
    chat_instancia.update_conversation(mensajes)

    # Afirmaciones
    assert chat_instancia.get_conversation_history() == mensajes


def test_recuperar_historial_conversacion():
    # Configuración
    chat_instancia = Chat()
    historial_conversacion = [ai.AIMessage(content="¡Hola!")]

    # Ejecución
    chat_instancia.update_conversation(historial_conversacion)
    historial_recuperado = chat_instancia.get_conversation_history()

    # Afirmaciones
    assert historial_recuperado == historial_conversacion


def test_manejo_audio_en_conversacion():
    # Configuración
    agente_mock = MagicMock()
    base_datos_mock = MagicMock()
    transcriptor_mock = MagicMock()
    id_conversacion_prueba = "id_de_prueba"
    archivo_audio = b"datos_audio"

    mock_conversacion = MagicMock()
    mock_conversacion.get_conversation_history.return_value = []
    mock_conversacion.id = id_conversacion_prueba
    base_datos_mock.get_chat.return_value = mock_conversacion

    transcriptor_mock.transcribe_audio.return_value = "Texto transcrito del audio"
    servicio_chat = ChatService(agent=agente_mock, db=base_datos_mock, transcriber=transcriptor_mock)

    # Ejecución
    respuesta = servicio_chat.continue_conversation(conversation_id=id_conversacion_prueba, voice_file=archivo_audio)

    # Afirmaciones
    transcriptor_mock.transcribe_audio.assert_called_once_with(archivo_audio)
    agente_mock.set_memory_variables.assert_called_once_with([])
    agente_mock.assert_called_once_with(query="Texto transcrito del audio")
    base_datos_mock.save_chat.assert_called_once()
    assert respuesta is not None



class TestRepositorioChat:
    def test_guardar_chat(self):
        # Configuración
        repositorio_mock = MagicMock(ChatRepository)
        chat_instancia = MagicMock(spec=Chat)

        # Ejecución
        repositorio_mock.save_chat(chat_instancia)

        # Afirmaciones
        repositorio_mock.save_chat.assert_called_once_with(chat_instancia)

    def test_recuperar_chat(self):
        # Configuración
        repositorio_mock = MagicMock(ChatRepository)
        chat_instancia = MagicMock(spec=Chat)
        repositorio_mock.get_chat.return_value = chat_instancia

        # Ejecución
        chat_recuperado = repositorio_mock.get_chat("id_chat_ejemp")

        # Afirmaciones
        assert chat_recuperado == chat_instancia
        repositorio_mock.get_chat.assert_called_once_with("id_chat_ejemp")

    def test_no_recuperar_chat(self):
        # Configuración
        repositorio_mock = MagicMock(ChatRepository)
        repositorio_mock.get_chat.return_value = None

        # Ejecución
        chat_recuperado = repositorio_mock.get_chat("id_chat_invalido")

        # Afirmaciones
        assert chat_recuperado is None
        repositorio_mock.get_chat.assert_called_once_with("id_chat_invalido")


class TestPuertoAgente:
    def test_establecer_variables_memoria(self):
        # Configuración
        agente_mock = MagicMock(AgentPort)
        historial = [ai.BaseMessage(type="usuario", content="Hola"), ai.BaseMessage(type="usuario", content="¡Hola mundo xd!")]

        # Ejecución
        agente_mock.set_memory_variables(historial)

        # Afirmaciones
        agente_mock.set_memory_variables.assert_called_once_with(historial)

    def test_manejo_consulta_agente(self):
        # Configuración
        agente_mock = MagicMock(AgentPort)
        agente_mock.side_effect = lambda consulta: {"respuesta": "¿Cómo puedo ayudarte?"}

        # Ejecución
        respuesta = agente_mock("Hola")

        # Afirmaciones
        assert respuesta == {"respuesta": "¿Cómo puedo ayudarte?"}
        agente_mock.assert_called_once_with("Hola")

    def test_recuperar_historial_conversacion(self):
        # Configuración
        agente_mock = MagicMock(AgentPort)
        historial_conversacion = [ai.BaseMessage(type="usuario", content="Hola"), ai.BaseMessage(type="usuario", content="¡Hola mundo jaja!")]
        agente_mock.get_conversation_history.return_value = historial_conversacion

        # Ejecución
        historial = agente_mock.get_conversation_history()

        # Afirmaciones
        assert historial == historial_conversacion
        agente_mock.get_conversation_history.assert_called_once()

    def test_recuperar_ultima_respuesta(self):
        # Configuración
        agente_mock = MagicMock(AgentPort)
        agente_mock.get_last_response.return_value = "¡ultima respuesta!"

        # Ejecución
        respuesta = agente_mock.get_last_response()

        # Afirmaciones
        assert respuesta == "¡ultima respuesta!"
        agente_mock.get_last_response.assert_called_once()

class TestTranscriptionPort:
    def test_transcribe_audio(self):
        # Configuración
        transcriptor_mock = MagicMock(spec=TranscriptionPort)
        transcriptor_mock.transcribe_audio.return_value = "Texto transcrito del audio"

        # Ejecución
        texto_transcrito = transcriptor_mock.transcribe_audio(b"datos_audio")

        # Afirmaciones
        assert texto_transcrito == "Texto transcrito del audio"
        transcriptor_mock.transcribe_audio.assert_called_once_with(b"datos_audio")

