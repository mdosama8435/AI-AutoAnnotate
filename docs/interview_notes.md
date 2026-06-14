# Interview Notes

This document is designed for technical interviewers reviewing the ExplainInk AI platform.

## Problem Statement
Creating high-quality educational explainer videos traditionally requires expensive hardware (tablets, styluses) and tedious manual video editing to synchronize drawings with voiceovers. ExplainInk AI automates this by deriving "intent" from natural speech and pairing it with visual structure recognition.

## Design Decisions
1. **Service-Oriented Architecture**: The system is split into distinct domains (`audio`, `ocr`, `llm`, `renderer`, `analytics`). This allows us to swap out Whisper for a different ASR model, or Gemini for GPT-4V, without rewriting the core pipeline.
2. **Pydantic Data Models**: All internal state is strictly typed using Pydantic V2. This guarantees that complex objects (like a `Transcript` with nested `TranscriptSegment` and `TranscriptWord`) are always valid before reaching the rendering engine.
3. **Human-in-the-Loop**: Fully autonomous AI is prone to hallucination. By integrating `st.data_editor`, we pause the pipeline before the LLM planner phase, allowing the user to correct OCR misclassifications or transcription errors.

## Trade-offs
1. **Synchronous Rendering vs Async Workers**: The current video rendering (`moviepy`) blocks the Streamlit thread. While simple to implement, this limits concurrency. In a true multi-tenant environment, video assembly must be offloaded to an asynchronous task queue (e.g., Celery).
2. **LLM Structured Output vs Speed**: We force the LLM to output pure JSON to map to our `AnnotationAction` schemas. This guarantees structural integrity but increases token latency compared to streaming text.

## Future Improvements
1. **Real-time Canvas Editing**: Move the timeline preview from a static Altair Gantt chart to a fully interactive React/Fabric.js canvas where users can drag bounding boxes directly on the video frame.
2. **Vector Graphics (SVG) Rendering**: Currently, the renderer uses OpenCV to draw pixels frame-by-frame. Exporting the timeline as a Lottie/SVG animation would drastically reduce rendering times and allow infinite scaling without pixelation.
