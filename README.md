# ExplainInk AI 🚀

ExplainInk AI is a production-grade educational video automation platform. It takes a raw question image and teacher narration, and generates a fully synchronized, animated explainer video automatically using state-of-the-art LLMs and Computer Vision.

## 🌟 Key Features
- **Semantic OCR**: Classifies image regions into math formulas, diagrams, and text using Gemini Vision.
- **Smart Planning**: Context-aware LLM generates a logical timeline of drawing actions (highlights, arrows, handwriting).
- **Teacher Analytics**: Analyzes pedagogical quality, speaking speed (WPM), and provides a comprehensive explanation summary.
- **Human-in-the-Loop**: Interactive Streamlit UI allows manual correction of OCR and transcripts before video rendering.

## 🏗️ Architecture

```mermaid
graph TD
    A[User Uploads Image + Audio] --> B(Storage Manager)
    B --> C{Pipeline Orchestrator}
    C --> D[OCR & Semantic Detector]
    C --> E[Whisper Transcriber]
    D --> F[NextGen Planner LLM]
    E --> F
    F --> G[Interactive Timeline UI]
    G --> H[Video Assembler & Painter]
    H --> I[Final MP4 Video]
```

## 🔄 Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant OCR
    participant Whisper
    participant Gemini
    participant Renderer

    User->>Streamlit: Upload Files
    Streamlit->>OCR: Extract & Classify Bounding Boxes
    Streamlit->>Whisper: Transcribe Audio to Word Timestamps
    OCR-->>Streamlit: Structured Visual Data
    Whisper-->>Streamlit: Structured Audio Data
    Streamlit->>User: Allow Smart Corrections
    User->>Streamlit: Confirm Edits
    Streamlit->>Gemini: Send Context for Planning
    Gemini-->>Streamlit: JSON Annotation Timeline
    Streamlit->>Renderer: Assemble Video (Progressive Drawing)
    Renderer-->>User: Final Rendered Video
```

## ⚙️ Setup & Deployment

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Environment Setup**: Add your `GEMINI_API_KEY` to a `.env` file.
3. **Run Locally**: `streamlit run app.py`

### Docker Deployment
Run using Docker Compose:
```bash
docker-compose up --build
```
Access the application at `http://localhost:8501`.

## 📚 Documentation Directory
- [System Design](docs/system_design.md)
- [Architecture Details](docs/architecture.md)
- [Scaling Strategy](docs/scaling_strategy.md)
- [Interview Notes (Design Decisions & Trade-offs)](docs/interview_notes.md)
