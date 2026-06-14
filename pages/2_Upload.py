import streamlit as st
import os
from src.storage.manager import StorageManager
from src.models.core import VideoProject
from src.utils.config import settings

st.set_page_config(page_title="Upload | ExplainInk AI", page_icon="📤", layout="wide")

st.title("Create New Project")

storage = StorageManager()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Upload Question Image")
    image_file = st.file_uploader("Upload Image (PNG, JPG)", type=["png", "jpg", "jpeg"])
    if image_file:
        st.image(image_file, caption="Preview", use_container_width=True)

with col2:
    st.markdown("### 2. Upload Narration Audio")
    audio_file = st.file_uploader("Upload Audio (MP3, WAV, M4A, MPEG)", type=["mp3", "wav", "m4a", "mpeg"])
    if audio_file:
        st.audio(audio_file)
        
st.markdown("### 3. Language & Settings")
language = st.selectbox("Audio Language", options=["English (en)", "Hindi (hi)", "Hinglish / Auto-detect (auto)"], index=2)
lang_code = "auto"
if "en" in language: lang_code = "en"
elif "hi" in language: lang_code = "hi"

if st.button("Initialize Project", type="primary"):
    if not image_file or not audio_file:
        st.error("Please upload both an image and an audio file.")
    else:
        with st.spinner("Initializing workspace..."):
            project_id = storage.create_project()
            
            img_path = storage.save_upload(project_id, f"base_image{os.path.splitext(image_file.name)[1]}", image_file.getvalue())
            aud_path = storage.save_upload(project_id, f"narration{os.path.splitext(audio_file.name)[1]}", audio_file.getvalue())
            
            project = VideoProject(
                project_id=project_id,
                image_path=img_path,
                audio_path=aud_path,
                language=lang_code
            )
            
            st.session_state.project_id = project_id
            st.session_state.project = project
            
            st.success(f"Project {project_id} initialized successfully!")
            st.info("Next: Go to OCR Analysis")
