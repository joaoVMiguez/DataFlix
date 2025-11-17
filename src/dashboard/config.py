"""Configurações do dashboard"""

import streamlit as st

CACHE_TTL = 3600  # 1 hora

def apply_page_config():
    """Aplica configurações da página"""
    st.set_page_config(
        page_title="DataFlix Analytics",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS customizado para design moderno estilo protótipo
    st.markdown("""
    <style>
    /* Remover padding extra */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Esconder sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Botões primários */
    .stButton>button[kind="primary"] {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #5568d3;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Botões normais */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        border-color: #667eea;
        color: #667eea;
    }
    
    /* Inputs */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        padding: 0.5rem 1rem;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background: transparent;
    }
    
    /* Remover decorações extras */
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #666;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        font-weight: 700;
    }
    
    /* Links no header */
    header a {
        color: #667eea !important;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s;
    }
    
    header a:hover {
        color: #5568d3 !important;
    }
    
    /* Gráficos */
    .js-plotly-plot {
        border-radius: 12px;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)