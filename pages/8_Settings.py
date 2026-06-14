import streamlit as st
import os
from src.utils.capabilities import check_ffmpeg, check_gpu

st.set_page_config(page_title="Settings | ExplainInk AI", page_icon="⚙️", layout="wide")

st.title("System Settings")

st.markdown("### API Keys")
api_key = st.text_input("Google Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
if st.button("Save API Key"):
    os.environ["GEMINI_API_KEY"] = api_key
    st.success("API Key saved to environment for this session.")

st.markdown("---")
st.markdown("### Capabilities Check")

col1, col2 = st.columns(2)

with col1:
    try:
        check_ffmpeg()
        st.success("✅ FFmpeg is installed and accessible.")
    except Exception as e:
        st.error(f"❌ FFmpeg check failed: {e}")

with col2:
    if check_gpu():
        st.success("✅ CUDA GPU detected. Models will run faster.")
    else:
        st.warning("⚠️ No CUDA GPU detected. CPU fallback active.")
        
st.markdown("---")
st.markdown("### Application Theme")
st.info("The application theme is managed via `.streamlit/config.toml`.")
st.code('''
[theme]
base="dark"
primaryColor="#F63366"
backgroundColor="#1E1E24"
secondaryBackgroundColor="#282A36"
textColor="#F8F8F2"
font="sans serif"
''', language="toml")
