import streamlit as st
import pandas as pd
import altair as alt
import os
from src.ui.theme import apply_theme
from src.llm.engines import NextGenPlanner, RuleBasedPlanner
from src.video.assembler import VideoAssembler
from src.storage.manager import StorageManager
from src.models.core import AnnotationAction
from src.utils.config import settings

st.set_page_config(page_title="Studio Workspace | ExplainInk AI", layout="wide")
apply_theme()

st.markdown("<h2 style='margin-bottom: 0;'>Studio Workspace</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: var(--muted-text);'>Edit timeline events, adjust timestamps, and render the final video.</p>", unsafe_allow_html=True)

if not st.session_state.get('project'):
    st.warning("Please initialize a project from the Upload page first.")
    st.stop()
    
project = st.session_state.project

# --- Top Action Bar ---
st.markdown("<div class='glass-card' style='margin-bottom: 1rem; display: flex; justify-content: space-between;'>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([1, 1, 1])

with col_a:
    btn_text = "✨ Auto-Plan with AI" if settings.gemini_api_key else "⚙️ Auto-Plan (Rule-Based)"
    if st.button(btn_text, type="secondary"):
        if project.transcript and project.ocr_result:
            if not settings.gemini_api_key:
                st.warning("Gemini API key unavailable. Running Rule-Based Planning.")
                
            with st.spinner("Analyzing context and generating timeline..."):
                try:
                    planner = NextGenPlanner() if settings.gemini_api_key else RuleBasedPlanner()
                    project.timeline = planner.generate_timeline(project.transcript, project.ocr_result)
                    st.session_state.project = project
                    st.rerun()
                except Exception as e:
                    st.error(f"Planning failed: {e}")
        else:
            st.error("Missing Transcript or OCR data.")
            
with col_c:
    if st.button("🎬 Render Final Video", type="primary"):
        if project.timeline:
            with st.spinner("Rendering advanced animations..."):
                storage = StorageManager()
                assembler = VideoAssembler(fps=30)
                out_path = storage.get_output_path(project.project_id)
                final_path = assembler.assemble(project.image_path, project.audio_path, project.timeline, out_path)
                project.output_video_path = final_path
                st.session_state.project = project
                st.success("Render Complete!")
        else:
            st.error("Timeline is empty. Please plan with AI or add events.")
st.markdown("</div>", unsafe_allow_html=True)

# Main Workspace Area - 3 Columns
col_img, col_gantt, col_editor = st.columns([2, 3, 3])

with col_img:
    st.markdown("#### Source Context")
    if project.image_path:
        st.image(project.image_path, use_container_width=True)
    if project.output_video_path and os.path.exists(project.output_video_path):
        st.markdown("#### Rendered Preview")
        # Handle start_time from session state for replay
        start_t = st.session_state.get("replay_start_time", 0.0)
        with open(project.output_video_path, 'rb') as vf:
            st.video(vf.read(), start_time=int(start_t))

with col_gantt:
    st.markdown("#### Timeline Preview")
    if project.timeline and project.timeline.actions:
        # Convert actions to DataFrame for Altair
        data = []
        for i, a in enumerate(project.timeline.actions):
            data.append({
                "Task": f"{a.action_type} ({i})",
                "Start": a.start_time,
                "End": a.end_time,
                "Color": a.color
            })
        df = pd.DataFrame(data)
        
        # Altair Gantt Chart
        chart = alt.Chart(df).mark_bar(cornerRadius=4, height=15).encode(
            x=alt.X('Start:Q', title='Time (seconds)'),
            x2='End:Q',
            y=alt.Y('Task:N', sort=alt.EncodingSortField(field="Start", order='ascending'), title='Events'),
            color=alt.Color('Color:N', scale=alt.Scale(scheme='category10'), legend=None),
            tooltip=['Task', 'Start', 'End']
        ).properties(
            height=400
        ).configure_axis(
            grid=True,
            gridColor="var(--border-color)",
            labelColor="var(--muted-text)",
            titleColor="var(--muted-text)"
        ).configure_view(
            strokeWidth=0
        ).configure_mark(
            opacity=0.8
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No timeline events to display. Use AI Planner to generate.")

with col_editor:
    st.markdown("#### Event Editor")
    st.caption("Drag columns to reorder. Double click cells to edit timing. Use the '+' at bottom to add.")
    
    if project.timeline and project.timeline.actions:
        # Load data into editable dataframe
        editor_data = []
        for a in project.timeline.actions:
            editor_data.append({
                "action_type": a.action_type,
                "start": a.start_time,
                "end": a.end_time,
                "color": a.color,
                "text": a.text if a.text else ""
            })
        df_edit = pd.DataFrame(editor_data)
        
        edited_df = st.data_editor(
            df_edit,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "action_type": st.column_config.SelectboxColumn(
                    "Action",
                    help="Type of annotation",
                    width="medium",
                    options=["highlight", "underline", "box", "circle", "arrow", "curved_arrow", "write_formula", "handwriting", "eraser"]
                ),
                "start": st.column_config.NumberColumn("Start (s)", format="%.2f", step=0.1),
                "end": st.column_config.NumberColumn("End (s)", format="%.2f", step=0.1),
                "color": st.column_config.SelectboxColumn(
                    "Color",
                    options=["red", "blue", "green", "yellow", "cyan", "magenta", "black", "white"]
                )
            }
        )
        
        if st.button("Save Timeline Changes"):
            # Reconstruct actions list
            new_actions = []
            for _, row in edited_df.iterrows():
                action = AnnotationAction(
                    action_type=row['action_type'],
                    start_time=row['start'],
                    end_time=row['end'],
                    color=row['color'],
                    text=row.get('text', "")
                )
                new_actions.append(action)
                
            project.timeline.actions = new_actions
            st.session_state.project = project
            st.success("Timeline updated!")
            st.rerun()
            
        st.markdown("#### Interactive Replay")
        st.caption("Click play to jump the video preview to this specific annotation.")
        for i, a in enumerate(project.timeline.actions):
            col_btn, col_info = st.columns([1, 4])
            with col_btn:
                if st.button("▶️", key=f"play_{i}"):
                    st.session_state.replay_start_time = a.start_time
                    st.rerun()
            with col_info:
                st.markdown(f"**{a.action_type}** at `{a.start_time:.1f}s`")
                
    else:
        st.info("Generate timeline first.")
