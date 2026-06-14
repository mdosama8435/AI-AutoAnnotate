import streamlit as st

def apply_theme():
    """Injects premium SaaS CSS styling into the Streamlit app."""
    
    # Check session state for theme, default to dark
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
        
    is_dark = st.session_state.theme_mode == "dark"
    
    # CSS Variables based on theme
    css_vars = f"""
    :root {{
        --bg-color: { "#0A0A0A" if is_dark else "#FAFAFA" };
        --card-bg: { "rgba(20, 20, 20, 0.7)" if is_dark else "rgba(255, 255, 255, 0.7)" };
        --text-color: { "#EDEDED" if is_dark else "#111111" };
        --muted-text: { "#A1A1A1" if is_dark else "#666666" };
        --border-color: { "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)" };
        --accent-color: { "#0070F3" if is_dark else "#0070F3" }; # Vercel Blue
        --skeleton-base: { "#222" if is_dark else "#eee" };
        --skeleton-shimmer: { "#333" if is_dark else "#f5f5f5" };
    }}
    """
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    {css_vars}

    /* Global Typography */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Hide top header and footer for cleaner look */
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    /* Layout padding adjustment for edge-to-edge feel */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }}

    /* Glassmorphism Cards */
    .glass-card {{
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }}
    
    /* Metric styling */
    div[data-testid="metric-container"] {{
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
    }}
    
    div[data-testid="metric-container"] label {{
        color: var(--muted-text) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }}
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        font-weight: 700 !important;
        font-size: 2rem !important;
        letter-spacing: -0.02em;
    }}

    /* Buttons - Vercel Style */
    .stButton > button {{
        background-color: var(--text-color) !important;
        color: var(--bg-color) !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        transform: scale(0.98);
        opacity: 0.9;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* Skeleton Loading Animation */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    .skeleton-loader {{
        animation: shimmer 2s infinite linear;
        background: linear-gradient(to right, var(--skeleton-base) 4%, var(--skeleton-shimmer) 25%, var(--skeleton-base) 36%);
        background-size: 1000px 100%;
        border-radius: 8px;
        height: 100px;
        margin-bottom: 16px;
    }}
    
    .skeleton-text {{
        height: 20px;
        margin-bottom: 8px;
        border-radius: 4px;
        width: 100%;
    }}
    .skeleton-text.short {{ width: 60%; }}
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
def toggle_theme():
    """Toggle between light and dark mode."""
    if st.session_state.theme_mode == "dark":
        st.session_state.theme_mode = "light"
    else:
        st.session_state.theme_mode = "dark"
