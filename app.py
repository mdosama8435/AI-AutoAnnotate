import streamlit as st
import os
from src.utils.config import settings

st.set_page_config(
    page_title=settings.app_name,
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'project_id' not in st.session_state:
    st.session_state.project_id = None
if 'project' not in st.session_state:
    st.session_state.project = None

st.title(f"Welcome to {settings.app_name} ✨")

st.markdown("""
### Transform Static Content into Dynamic Explainer Videos

ExplainInk AI uses advanced Machine Learning to automatically synchronize a teacher's audio narration with visual annotations on a static image.

**How it works:**
1. **Upload**: Provide a static question image and an audio recording of the explanation.
2. **OCR Analysis**: We detect text and equations in the image.
3. **Transcript**: Whisper transcribes the audio with word-level timestamps.
4. **LLM Planner**: Gemini analyzes the transcript and OCR to plan visual annotations (highlights, underlines).
5. **Video Assembly**: We render the annotations over time and stitch it with the audio.

👈 Get started by navigating to the **Upload** page in the sidebar!
""")

st.info("Tip: Ensure you have your Google Gemini API Key configured in your environment or settings.")
