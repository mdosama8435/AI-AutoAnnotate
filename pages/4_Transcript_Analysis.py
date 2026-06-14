import streamlit as st
import pandas as pd
from src.audio.transcriber import AudioTranscriber
from src.ui.theme import apply_theme

st.set_page_config(page_title="Transcript Analysis | ExplainInk AI", layout="wide")
apply_theme()

st.title("Transcript Analysis")
st.markdown("<p style='color: var(--muted-text);'>Transcribe audio using Faster-Whisper. <b>Smart Correction:</b> Edit segments manually to fix transcription errors.</p>", unsafe_allow_html=True)

if not st.session_state.get('project'):
    st.warning("Please initialize a project from the Upload page first.")
    st.stop()
    
project = st.session_state.project

col1, col2 = st.columns([1, 1])
with col1:
    st.audio(project.audio_path)
with col2:
    if st.button("Run Whisper Transcription", type="primary"):
        with st.spinner("Transcribing audio..."):
            try:
                transcriber = AudioTranscriber()
                transcript = transcriber.transcribe(project.audio_path, language=project.language)
                project.transcript = transcript
                st.session_state.project = project
                st.success("Transcription complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Transcription Failed: {e}")

if project.transcript:
    st.markdown("---")
    st.markdown("### Smart Correction Mode")
    st.caption("Double-click text to manually correct transcription errors before LLM planning.")
    
    data = []
    for seg in project.transcript.segments:
        data.append({
            "Start": seg.start,
            "End": seg.end,
            "Text": seg.text
        })
        
    df = pd.DataFrame(data)
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Start": st.column_config.NumberColumn("Start (s)", format="%.2f"),
            "End": st.column_config.NumberColumn("End (s)", format="%.2f"),
            "Text": st.column_config.TextColumn("Text")
        }
    )
    
    if st.button("Save Transcript Corrections"):
        for i, row in edited_df.iterrows():
            project.transcript.segments[i].text = row["Text"]
            project.transcript.segments[i].start = row["Start"]
            project.transcript.segments[i].end = row["End"]
            
        # Update full text
        project.transcript.text = " ".join([s.text for s in project.transcript.segments])
        st.session_state.project = project
        st.success("Transcript corrections saved!")
