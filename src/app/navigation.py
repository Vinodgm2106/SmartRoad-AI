import streamlit as st

def render_sidebar(active_page):
    st.sidebar.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 10px; padding-top: 15px; width: 100%;">
            <a href="/" target="_self" class="nav-item-expanded {'active' if active_page == 'Home' else ''}">
                <span class="nav-icon">🏠</span>
                <span class="nav-text">Home Portal</span>
            </a>
            <a href="/Dashboard" target="_self" class="nav-item-expanded {'active' if active_page == 'Dashboard' else ''}">
                <span class="nav-icon">🖥️</span>
                <span class="nav-text">Executive Dashboard</span>
            </a>
            <a href="/Detection" target="_self" class="nav-item-expanded {'active' if active_page == 'Detection' else ''}">
                <span class="nav-icon">🔍</span>
                <span class="nav-text">Detection Interface</span>
            </a>
            <a href="/Video_Analysis" target="_self" class="nav-item-expanded {'active' if active_page == 'Video Analysis' else ''}">
                <span class="nav-icon">🎥</span>
                <span class="nav-text">Video Analysis</span>
            </a>
            <a href="/Analytics" target="_self" class="nav-item-expanded {'active' if active_page == 'Analytics' else ''}">
                <span class="nav-icon">📈</span>
                <span class="nav-text">Analytics Deep-Dive</span>
            </a>
            <a href="/History" target="_self" class="nav-item-expanded {'active' if active_page == 'History' else ''}">
                <span class="nav-icon">📜</span>
                <span class="nav-text">Inspection Logs</span>
            </a>
            <a href="/AI_Assistant" target="_self" class="nav-item-expanded {'active' if active_page == 'AI Assistant' else ''}">
                <span class="nav-icon">💬</span>
                <span class="nav-text">AI Assistant</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
