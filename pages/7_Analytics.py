import streamlit as st
import altair as alt
import pandas as pd
from src.ui.theme import apply_theme
from src.analytics.insights import AnalyticsEngine

st.set_page_config(page_title="Teacher Analytics | ExplainInk AI", layout="wide")
apply_theme()

st.title("Teacher Analytics & AI Summary")

if not st.session_state.get('project'):
    st.warning("Please initialize a project first.")
    st.stop()
    
project = st.session_state.project

if st.button("Generate Deep Insights", type="primary"):
    with st.spinner("AI is analyzing teaching patterns..."):
        engine = AnalyticsEngine()
        project.analytics = engine.generate_analytics(project)
        st.session_state.project = project
        st.success("Analysis Complete!")

if project.analytics:
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### AI Explanation Summary")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # Quality Score Gauge simulation
        score = project.analytics.explanation_quality_score
        color = "#00ff00" if score > 80 else "#ffa500" if score > 60 else "#ff0000"
        st.markdown(f"<h1 style='text-align: center; color: {color}; margin-bottom: 0;'>{score}/100</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: var(--muted-text); margin-top: 0;'>Explanation Quality</p>", unsafe_allow_html=True)
        
        if project.analytics.summary:
            sum_data = project.analytics.summary
            st.markdown(f"**Difficulty:** {sum_data.difficulty_level}")
            st.markdown("**Key Concepts:**")
            for c in sum_data.key_concepts: st.markdown(f"- {c}")
            st.markdown("**Formulas Used:**")
            for f in sum_data.formula_used: st.markdown(f"- {f}")
            if sum_data.final_answer:
                st.markdown(f"**Final Answer:** {sum_data.final_answer}")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### Teaching Metrics")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Speaking Speed", f"{project.analytics.wpm} WPM")
        with m2: st.metric("Total Pauses", f"{project.analytics.total_pause_duration}s")
        with m3: st.metric("Annotation Density", f"{project.analytics.annotation_density} actions/min")
        
        st.markdown("#### Pacing Over Time")
        # Visualizing pacing by plotting segment lengths over time
        if project.transcript:
            data = []
            for seg in project.transcript.segments:
                duration = seg.end - seg.start
                wpm_seg = (len(seg.text.split()) / duration) * 60 if duration > 0 else 0
                data.append({"Time (s)": seg.start, "WPM": wpm_seg})
                
            df = pd.DataFrame(data)
            chart = alt.Chart(df).mark_area(
                color="var(--accent-color)", opacity=0.3, line=True
            ).encode(
                x='Time (s):Q',
                y='WPM:Q',
                tooltip=['Time (s)', 'WPM']
            ).properties(height=250).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
