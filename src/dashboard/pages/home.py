"""Página Home - Visão Geral"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import movielens, tmdb, box_office
from dashboard.components import sidebar

# ==================== SIDEBAR ====================
sidebar.render_sidebar_header()
st.sidebar.markdown("### 🏠 Página Inicial")
st.sidebar.info("**Visão geral** de todos os datasets disponíveis")
sidebar.render_sidebar_footer()

# ==================== HEADER ====================
st.title("🎬 DataFlix Analytics - Visão Geral")
st.markdown("**Dashboard completo** de análise de filmes com dados de múltiplas fontes")
st.markdown("---")

# ==================== STATS GERAIS ====================
st.header("📊 Estatísticas Globais")

# MovieLens
ml_stats = movielens.get_stats()
ml_min, ml_max = movielens.get_year_range()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🎬 MovieLens")
    st.metric("Filmes", f"{ml_stats['total_movies']:,}")
    st.metric("Avaliações", f"{ml_stats['total_ratings']:,}")
    st.metric("Média", f"{ml_stats['avg_rating']} ⭐")
    st.caption(f"📅 {ml_min} - {ml_max}")

# TMDB
has_tmdb = tmdb.check_tmdb_data()
with col2:
    st.markdown("### 📊 TMDB")
    if has_tmdb:
        tmdb_stats = tmdb.get_stats()
        st.metric("Filmes", f"{tmdb_stats['total_movies']:,}")
        st.metric("Receita", f"${tmdb_stats['total_revenue']/1e9:.1f}B")
        st.metric("Orçamento", f"${tmdb_stats['total_budget']/1e9:.1f}B")
        tmdb_min, tmdb_max = tmdb.get_year_range()
        st.caption(f"📅 {tmdb_min} - {tmdb_max}")
    else:
        st.info("📭 Dados TMDB não disponíveis")

# Box Office
has_box = box_office.check_box_office_data()
with col3:
    st.markdown("### 💰 Box Office")
    if has_box:
        box_stats = box_office.get_stats()
        st.metric("Filmes", f"{box_stats['total_movies']:,}")
        st.metric("Lucro", f"${box_stats['total_profit']/1e9:.1f}B")
        st.metric("Lucrativos", f"{box_stats['profitable_count']:,}")
        box_min, box_max = box_office.get_year_range()
        st.caption(f"📅 {box_min} - {box_max}")
    else:
        st.info("📭 Dados Box Office não disponíveis")

st.markdown("---")

# ==================== DESTAQUES ====================
st.header("🏆 Destaques")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Top 5 Mais Bem Avaliados (MovieLens)")
    top_ml = movielens.get_top_movies(5)
    for idx, row in top_ml.iterrows():
        st.markdown(f"**{idx+1}.** {row['title']} ({row['release_year']}) - {row['avg_rating']}⭐")

with col2:
    if has_tmdb:
        st.subheader("💰 Top 5 Maior Receita (TMDB)")
        top_revenue = tmdb.get_top_revenue_movies(5)
        for idx, row in top_revenue.iterrows():
            st.markdown(f"**{idx+1}.** {row['title']} ({row['release_year']}) - ${row['revenue']/1e6:.1f}M")
    else:
        st.info("📭 Dados TMDB não disponíveis")

st.markdown("---")

# ==================== NAVEGAÇÃO RÁPIDA ====================
st.header("🚀 Navegação Rápida")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        ### 🎬 MovieLens
        Análise detalhada de avaliações de usuários
        
        **Recursos:**
        - Top filmes por avaliação
        - Análise por década
        - Gêneros mais populares
        - Busca avançada
        """
    )

with col2:
    if has_tmdb:
        st.markdown(
            """
            ### 📊 TMDB
            Metadados completos de filmes
            
            **Recursos:**
            - Receitas e orçamentos
            - Evolução temporal
            - Comparações financeiras
            - Dados de produção
            """
        )
    else:
        st.info("📭 Dados não disponíveis")

with col3:
    if has_box:
        st.markdown(
            """
            ### 💰 Box Office
            Análise de performance financeira
            
            **Recursos:**
            - Filmes mais lucrativos
            - Taxa de sucesso
            - ROI e rentabilidade
            - Blockbusters
            """
        )
    else:
        st.info("📭 Dados não disponíveis")

st.markdown("---")

# ==================== INFORMAÇÕES DO SISTEMA ====================
st.header("ℹ️ Sobre o DataFlix")

st.markdown(
    """
    O **DataFlix Analytics** é um dashboard completo para análise de filmes, combinando dados de:
    
    - **MovieLens**: Avaliações de usuários reais
    - **TMDB**: Metadados e informações financeiras
    - **Box Office**: Performance de bilheteria
    
    **Tecnologias utilizadas:**
    - 🐍 Python 3.13
    - 🎨 Streamlit
    - 🐘 PostgreSQL
    - 📊 Plotly
    - 🔄 Apache Airflow (ETL)
    
    **Desenvolvido por:** DataFlix Team 🎬
    """
)