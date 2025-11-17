"""Página Home - Estilo Protótipo Moderno"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import tmdb, box_office
from dashboard.components import navigation

# ==================== NAVEGAÇÃO ====================
navigation.render_navigation("home")

# Hero Section
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='font-size: 3.5rem; margin: 0; font-weight: 800;'>DataFlix Analytics</h1>
    <p style='color: #666; font-size: 1.1rem; margin-top: 1rem;'>
        Explore insights de milhões de filmes, avaliações e performance de<br>bilheteria através de análises avançadas de dados
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Cards dos Datasets
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: white; border-radius: 16px; padding: 2rem; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;
                height: 280px; display: flex; flex-direction: column;'>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    width: 56px; height: 56px; border-radius: 12px; display: flex;
                    align-items: center; justify-content: center; margin-bottom: 1.5rem;'>
            <span style='color: white; font-size: 1.8rem;'>🎬</span>
        </div>
        <h3 style='margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700;'>MovieLens</h3>
        <p style='color: #666; margin: 0 0 1rem 0; font-size: 0.95rem; flex-grow: 1;'>
            Catálogo completo de filmes e avaliações de usuários
        </p>
        <p style='color: #667eea; margin: 0 0 1rem 0; font-size: 0.85rem; font-weight: 600;'>
            Milhares de filmes • Milhões de avaliações
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Explorar MovieLens →", key="btn_ml", use_container_width=True, type="primary"):
        st.switch_page("pages/movielens.py")

with col2:
    has_tmdb = tmdb.check_tmdb_data()
    
    st.markdown("""
    <div style='background: white; border-radius: 16px; padding: 2rem; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;
                height: 280px; display: flex; flex-direction: column;'>
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    width: 56px; height: 56px; border-radius: 12px; display: flex;
                    align-items: center; justify-content: center; margin-bottom: 1.5rem;'>
            <span style='color: white; font-size: 1.8rem;'>📊</span>
        </div>
        <h3 style='margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700;'>TMDB</h3>
        <p style='color: #666; margin: 0 0 1rem 0; font-size: 0.95rem; flex-grow: 1;'>
            Metadados detalhados e análise de receita
        </p>
        <p style='color: #f5576c; margin: 0 0 1rem 0; font-size: 0.85rem; font-weight: 600;'>
            Receitas • Orçamentos • Popularidade
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if has_tmdb:
        if st.button("Explorar TMDB →", key="btn_tmdb", use_container_width=True, type="primary"):
            st.switch_page("pages/tmdb.py")
    else:
        st.button("Dados não disponíveis", key="btn_tmdb_disabled", use_container_width=True, disabled=True)

with col3:
    has_box = box_office.check_box_office_data()
    
    st.markdown("""
    <div style='background: white; border-radius: 16px; padding: 2rem; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;
                height: 280px; display: flex; flex-direction: column;'>
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    width: 56px; height: 56px; border-radius: 12px; display: flex;
                    align-items: center; justify-content: center; margin-bottom: 1.5rem;'>
            <span style='color: white; font-size: 1.8rem;'>💰</span>
        </div>
        <h3 style='margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700;'>Box Office</h3>
        <p style='color: #666; margin: 0 0 1rem 0; font-size: 0.95rem; flex-grow: 1;'>
            Análise financeira e performance de bilheteria
        </p>
        <p style='color: #00f2fe; margin: 0 0 1rem 0; font-size: 0.85rem; font-weight: 600;'>
            Lucratividade • ROI • Blockbusters
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if has_box:
        if st.button("Explorar Box Office →", key="btn_box", use_container_width=True, type="primary"):
            st.switch_page("pages/box_office.py")
    else:
        st.button("Dados não disponíveis", key="btn_box_disabled", use_container_width=True, disabled=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Seção de Recursos
st.markdown("""
<div style='text-align: center; margin: 3rem 0 2rem 0;'>
    <h2 style='font-size: 2rem; font-weight: 700;'>Recursos da Plataforma</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <div style='background: #eff6ff; width: 64px; height: 64px; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 1rem auto;'>
            <span style='font-size: 2rem;'>⭐</span>
        </div>
        <h4 style='margin: 0 0 0.5rem 0; font-weight: 700;'>Análise de Avaliações</h4>
        <p style='color: #666; font-size: 0.9rem; margin: 0;'>
            Descubra os filmes mais bem avaliados e tendências de preferência do público
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <div style='background: #f0fdf4; width: 64px; height: 64px; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 1rem auto;'>
            <span style='font-size: 2rem;'>📈</span>
        </div>
        <h4 style='margin: 0 0 0.5rem 0; font-weight: 700;'>Performance Financeira</h4>
        <p style='color: #666; font-size: 0.9rem; margin: 0;'>
            Analise receitas, orçamentos e identifique os maiores sucessos de bilheteria
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <div style='background: #fef3c7; width: 64px; height: 64px; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 1rem auto;'>
            <span style='font-size: 2rem;'>📊</span>
        </div>
        <h4 style='margin: 0 0 0.5rem 0; font-weight: 700;'>Insights Temporais</h4>
        <p style='color: #666; font-size: 0.9rem; margin: 0;'>
            Explore evolução de gêneros, décadas e tendências do cinema ao longo do tempo
        </p>
    </div>
    """, unsafe_allow_html=True)