import streamlit as st
import cv2
import pandas as pd
from src.ocr.detector import OCRDetector
from src.ocr.semantic import SemanticDetector
from src.ui.theme import apply_theme

st.set_page_config(page_title="OCR Analysis | ExplainInk AI", layout="wide")
apply_theme()

st.title("OCR & Semantic Analysis")
st.markdown("<p style='color: var(--muted-text);'>Detect bounding boxes and semantically classify them. <b>Smart Correction:</b> Edit the table below to fix AI mistakes before planning.</p>", unsafe_allow_html=True)

if not st.session_state.get('project'):
    st.warning("Please initialize a project from the Upload page first.")
    st.stop()
    
project = st.session_state.project

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Run OCR Detection", type="primary"):
        with st.spinner("Analyzing image structure and semantics..."):
            try:
                detector = OCRDetector()
                base_result = detector.extract_elements(project.image_path)
                semantic = SemanticDetector()
                project.ocr_result = semantic.classify_elements(project.image_path, base_result)
                st.session_state.project = project
                st.success(f"Detected {len(project.ocr_result.elements)} regions.")
                st.rerun()
            except Exception as e:
                st.error(f"OCR Failed: {e}")

if project.ocr_result:
    st.markdown("---")
    col_img, col_data = st.columns([1, 1])
    
    with col_img:
        st.markdown("### Detection Map")
        img = cv2.imread(project.image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        for i, el in enumerate(project.ocr_result.elements):
            color = (0, 255, 0)
            if el.semantic_type == "math_formula": color = (255, 0, 0)
            elif el.semantic_type == "mcq_option": color = (0, 0, 255)
            
            cv2.rectangle(
                img_rgb, 
                (el.box.x_min, el.box.y_min), 
                (el.box.x_max, el.box.y_max), 
                color, 2
            )
            cv2.putText(
                img_rgb, el.id, 
                (el.box.x_min, el.box.y_min - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
            
        st.image(img_rgb, use_container_width=True)

    with col_data:
        st.markdown("### Smart Correction Mode")
        st.caption("Double-click any cell to manually correct the OCR text or classification type.")
        
        data = []
        for el in project.ocr_result.elements:
            data.append({
                "ID": el.id,
                "Text": el.text,
                "Type": el.semantic_type,
                "Confidence": f"{el.confidence * 100:.1f}%"
            })
            
        df = pd.DataFrame(data)
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", disabled=True),
                "Type": st.column_config.SelectboxColumn("Type", options=["math_formula", "diagram", "mcq_option", "general_text"]),
                "Confidence": st.column_config.TextColumn("Confidence", disabled=True)
            }
        )
        
        if st.button("Save Corrections"):
            for i, row in edited_df.iterrows():
                project.ocr_result.elements[i].text = row["Text"]
                project.ocr_result.elements[i].semantic_type = row["Type"]
            st.session_state.project = project
            st.success("Corrections saved!")
