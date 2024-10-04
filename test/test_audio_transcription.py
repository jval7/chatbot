from unittest.mock import Mock, patch
from app.adapters.audio_transcription import OpenAITranscriptionClient


def test_transcribe_audio():
    mock_response = Mock()
    mock_response.json.return_value = {"text": "Test transcription"}
    mock_response.status_code = 200
    with patch("app.adapters.audio_transcription.requests.Session.post", return_value=mock_response):
        client = OpenAITranscriptionClient(
            api_key="test_key",
            api_url="https://api.openai.com/v1/transcriptions",
            transcription_model="whisper-1"
        )
        result = client.transcribe_audio(b"audio data")
        assert result == "Test transcription"
