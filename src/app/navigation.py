import streamlit as st

def render_sidebar(active_page):
    st.sidebar.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; padding-top: 20px; width: 100%;">
            <div class="nav-item-container">
                <a href="/" target="_self" class="nav-item {'active' if active_page == 'Home' else ''}" data-tooltip="Home Portal">
                    <span>🏠</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/Dashboard" target="_self" class="nav-item {'active' if active_page == 'Dashboard' else ''}" data-tooltip="Executive Dashboard">
                    <span>🖥️</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/Detection" target="_self" class="nav-item {'active' if active_page == 'Detection' else ''}" data-tooltip="Detection Interface">
                    <span>🔍</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/Video_Analysis" target="_self" class="nav-item {'active' if active_page == 'Video Analysis' else ''}" data-tooltip="Video Analysis">
                    <span>🎥</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/Analytics" target="_self" class="nav-item {'active' if active_page == 'Analytics' else ''}" data-tooltip="Analytics Deep-Dive">
                    <span>📈</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/History" target="_self" class="nav-item {'active' if active_page == 'History' else ''}" data-tooltip="History Logs">
                    <span>📜</span>
                </a>
            </div>
            <div class="nav-item-container">
                <a href="/AI_Assistant" target="_self" class="nav-item {'active' if active_page == 'AI Assistant' else ''}" data-tooltip="AI Chatbot Assistant">
                    <span>💬</span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
