import pytest
from unittest.mock import MagicMock
from src.pipeline.orchestrator import PipelineOrchestrator
from src.models.core import VideoProject, OCRResult, Timeline, Transcript

def test_pipeline_process_success(mocker):
    # Mock all internal services to avoid actual computation
    mocker.patch("src.pipeline.orchestrator.StorageManager")
    mock_ocr = mocker.patch("src.pipeline.orchestrator.OCRDetector").return_value
    mock_semantic = mocker.patch("src.pipeline.orchestrator.SemanticDetector").return_value
    mock_audio = mocker.patch("src.pipeline.orchestrator.AudioTranscriber").return_value
    mock_planner = mocker.patch("src.pipeline.orchestrator.NextGenPlanner").return_value
    mock_video = mocker.patch("src.pipeline.orchestrator.VideoAssembler").return_value
    
    # Setup mock returns
    mock_ocr.extract_elements.return_value = OCRResult(elements=[], image_width=100, image_height=100)
    mock_semantic.classify_elements.return_value = OCRResult(elements=[], image_width=100, image_height=100)
    mock_audio.transcribe.return_value = Transcript(text="test", segments=[])
    mock_planner.generate_timeline.return_value = Timeline(actions=[], duration=10.0)
    mock_video.assemble.return_value = "output.mp4"
    
    orchestrator = PipelineOrchestrator()
    
    project = VideoProject(
        project_id="test_proj",
        image_path="test.png",
        audio_path="test.mp3"
    )
    
    # Run pipeline
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("json.dump")
    
    result = orchestrator.process(project)
    
    assert result.project_id == "test_proj"
    assert result.transcript.text == "test"
    assert result.output_video_path == "output.mp4"
    assert mock_planner.generate_timeline.called
    assert mock_video.assemble.called
