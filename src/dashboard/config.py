"""Configurações do dashboard"""

import streamlit as st

CACHE_TTL = 3600  # 1 hora

def apply_page_config():
    """Aplica configurações da página"""
    st.set_page_config(
        page_title="DataFlix Analytics",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )