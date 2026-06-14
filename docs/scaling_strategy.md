# Scaling Strategy

While Streamlit is phenomenal for rapid prototyping and internal tooling, it is fundamentally synchronous and state-bound to the active WebSocket session. To scale ExplainInk AI for thousands of concurrent students and teachers, we propose the following architectural migration:

## Target Architecture

1. **Frontend (React / Next.js)**
   - Replaces Streamlit.
   - Provides a true HTML5 Canvas editor for real-time bounding box adjustments.
   
2. **API Layer (FastAPI)**
   - Replaces the Streamlit Python backend.
   - Stateless REST/GraphQL endpoints.
   - Handles authentication and dispatches heavy jobs to the message queue.
   
3. **Task Queue (Celery + Redis)**
   - The `PipelineOrchestrator` is moved here.
   - Audio Transcription (Whisper) and Video Rendering (MoviePy/OpenCV) are extremely CPU/GPU intensive. By moving them to Celery workers, we prevent API blockage.
   
4. **Storage (AWS S3 + PostgreSQL)**
   - `StorageManager` currently writes to the local disk. In production, base images and final videos must be streamed directly to S3.
   - `VideoProject` state transitions from JSON/Pickle files into a PostgreSQL relational database.
