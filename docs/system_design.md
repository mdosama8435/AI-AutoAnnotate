# System Design

## Data Models
We utilize **Pydantic V2** to enforce strict typing across the entire pipeline. 
The central data structure is `VideoProject`, which travels through the system.

```python
class VideoProject(BaseModel):
    project_id: str
    image_path: str
    audio_path: str
    transcript: Optional[Transcript]
    ocr_result: Optional[OCRResult]
    timeline: Optional[Timeline]
    analytics: Optional[TeacherAnalytics]
```

## State Management
Streamlit is inherently stateless between re-runs. To overcome this, the `VideoProject` is serialized and stored in `st.session_state`. When a user edits a transcription in the Smart Correction UI, it mutates the `st.session_state.project.transcript` object instantly.
