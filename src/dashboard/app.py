"""
🎬 DataFlix Analytics Dashboard
"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.config import apply_page_config
from dashboard.data import tmdb, box_office

# ==================== CONFIG ====================
apply_page_config()

# ==================== VERIFICAR DADOS ====================
has_tmdb = tmdb.check_tmdb_data()
has_box_office = box_office.check_box_office_data()

# ==================== CAMINHOS ====================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(CURRENT_DIR, "pages")

# ==================== PÁGINAS ====================
pages_dict = {
    "🏠 Home": [
        st.Page(os.path.join(PAGES_DIR, "home.py"), title="Home", icon="🏠", default=True)
    ],
    "📊 Análises": [
        st.Page(os.path.join(PAGES_DIR, "movielens.py"), title="MovieLens", icon="🎬")
    ]
}

if has_tmdb:
    pages_dict["📊 Análises"].append(
        st.Page(os.path.join(PAGES_DIR, "tmdb.py"), title="TMDB", icon="📊")
    )

if has_box_office:
    pages_dict["📊 Análises"].append(
        st.Page(os.path.join(PAGES_DIR, "box_office.py"), title="Box Office", icon="💰")
    )

# ==================== NAVEGAÇÃO ====================
pg = st.navigation(pages_dict)
pg.run()