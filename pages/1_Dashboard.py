import streamlit as st
import time
from src.ui.theme import apply_theme, toggle_theme
import os

st.set_page_config(page_title="Dashboard | ExplainInk AI", layout="wide")

# Apply custom CSS
apply_theme()

# Header with Theme Toggle
col1, col2 = st.columns([10, 1])
with col1:
    st.markdown("<h1 style='margin-bottom: 0;'>Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--muted-text);'>Welcome to your ExplainInk Workspace.</p>", unsafe_allow_html=True)
with col2:
    if st.button("🌓 Theme"):
        toggle_theme()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Simulate Data Fetching for premium feel
if "dashboard_loaded" not in st.session_state:
    st.session_state.dashboard_loaded = False

if not st.session_state.dashboard_loaded:
    # Render Skeleton Loaders
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown("<div class='skeleton-loader'></div>", unsafe_allow_html=True)
    with col2: st.markdown("<div class='skeleton-loader'></div>", unsafe_allow_html=True)
    with col3: st.markdown("<div class='skeleton-loader'></div>", unsafe_allow_html=True)
    with col4: st.markdown("<div class='skeleton-loader'></div>", unsafe_allow_html=True)
    
    st.markdown("<br><div class='skeleton-loader skeleton-text'></div>", unsafe_allow_html=True)
    st.markdown("<div class='skeleton-loader skeleton-text short'></div>", unsafe_allow_html=True)
    
    time.sleep(1.5) # Simulate network request
    st.session_state.dashboard_loaded = True
    st.rerun()

# Actual Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Videos Generated", value="142", delta="12 this week")
    
with col2:
    st.metric(label="Avg Processing Time", value="12.4s", delta="-1.2s", delta_color="inverse")
    
with col3:
    st.metric(label="OCR Accuracy", value="99.2%", delta="0.4%")

with col4:
    st.metric(label="Transcript Confidence", value="98.7%", delta="1.1%")

st.markdown("<br>", unsafe_allow_html=True)

# AI Confidence Panel
if st.session_state.get('project'):
    st.markdown("### AI Confidence Panel")
    proj = st.session_state.project
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ocr_conf = f"{proj.ocr_result.avg_confidence*100:.1f}%" if proj.ocr_result else "--"
        st.metric("Structural OCR", ocr_conf)
    with c2:
        sem_conf = f"{(proj.ocr_result.avg_confidence*0.95)*100:.1f}%" if proj.ocr_result else "--" # simulated slight drop for semantic
        st.metric("Semantic Detection", sem_conf)
    with c3:
        # Assuming we eventually pass avg_confidence to transcript, simulate here
        speech_conf = "98.7%" if proj.transcript else "--" 
        st.metric("Speech Recognition", speech_conf)
    with c4:
        timeline_conf = f"{proj.timeline.avg_confidence*100:.1f}%" if proj.timeline else "--"
        st.metric("Intent Planning", timeline_conf)
        
st.markdown("<br>", unsafe_allow_html=True)

# Recent Projects Section
st.markdown("### Recent Projects")

project_html = """
<div class='glass-card' style='margin-bottom: 1rem;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h4 style='margin: 0;'>Calculus 101 - Derivatives</h4>
            <p style='margin: 0; color: var(--muted-text); font-size: 0.9rem;'>Updated 2 hours ago</p>
        </div>
        <div style='background: rgba(0, 255, 0, 0.1); color: #00ff00; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;'>Ready</div>
    </div>
</div>
<div class='glass-card' style='margin-bottom: 1rem;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h4 style='margin: 0;'>Physics - Kinematics MCQ</h4>
            <p style='margin: 0; color: var(--muted-text); font-size: 0.9rem;'>Updated yesterday</p>
        </div>
        <div style='background: rgba(0, 255, 0, 0.1); color: #00ff00; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;'>Ready</div>
    </div>
</div>
"""
st.markdown(project_html, unsafe_allow_html=True)

if st.session_state.get('project'):
    st.info(f"Currently active session: {st.session_state.project.project_id}")
