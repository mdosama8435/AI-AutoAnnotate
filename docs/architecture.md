# Architecture Details

ExplainInk AI follows a modular, Service-Oriented Architecture (SOA) pattern, dividing complex video generation logic into independent functional domains.

## Directory Structure
- `src/audio/`: Wraps Faster-Whisper. Handles all ASR and word-level timestamp generation.
- `src/ocr/`: Wraps OpenCV and Gemini Vision. Extracts bounding boxes and determines semantic meaning.
- `src/llm/`: The orchestrator of logic. Takes semantic visual data and timestamped audio data to synthesize a timeline.
- `src/renderer/`: Pure graphics logic. Stateless functions that take instructions and yield modified frames.
- `src/pipeline/`: The master controller linking all services sequentially.

## Dependency Injection
The `PipelineOrchestrator` uses constructor injection to load its engines. This makes it trivial to swap out `AudioTranscriber` for a cloud-based `GoogleCloudSTT` class in the future without changing the orchestrator logic.
