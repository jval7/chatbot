from unittest.mock import Mock, patch
from app.adapters.audio_transcription import OpenAITranscriptionClient


@patch('app.adapters.audio_transcription.requests.Session')
def test_transcribe_audio(mock_session):
    # Mockear la respuesta del API
    mock_response = Mock()
    mock_response.json.return_value = {"text": "Transcripción exitosa"}
    mock_response.raise_for_status = Mock()

    mock_session.return_value.post.return_value = mock_response

    client = OpenAITranscriptionClient(api_key="fake_key", api_url="fake_url", transcription_model="fake_model")
    result = client.transcribe_audio(b"fake_audio_data")

    assert result == "Transcripción exitosa"
    mock_session.return_value.post.assert_called_once()