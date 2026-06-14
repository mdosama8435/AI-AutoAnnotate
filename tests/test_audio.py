import pytest
from unittest.mock import MagicMock
from src.audio.transcriber import AudioTranscriber
from src.models.core import Transcript

def test_transcribe_success(mocker):
    # Mock the WhisperModel initialization
    mock_model_class = mocker.patch("src.audio.transcriber.WhisperModel")
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance
    
    # Mock the return value of transcribe
    mock_segment = MagicMock()
    mock_segment.id = "1"
    mock_segment.text = "Hello world"
    mock_segment.start = 0.0
    mock_segment.end = 1.0
    mock_segment.words = []
    
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99
    
    mock_model_instance.transcribe.return_value = ([mock_segment], mock_info)
    
    # Mock os.path.exists to bypass file check
    mocker.patch("os.path.exists", return_value=True)
    
    transcriber = AudioTranscriber()
    transcript = transcriber.transcribe("dummy.mp3")
    
    assert isinstance(transcript, Transcript)
    assert transcript.text == "Hello world"
    assert len(transcript.segments) == 1
    assert transcript.segments[0].start == 0.0

def test_transcribe_file_not_found():
    transcriber = AudioTranscriber()
    with pytest.raises(Exception, match="Audio file not found"):
        transcriber.transcribe("nonexistent.mp3")
