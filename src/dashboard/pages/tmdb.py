"""Página TMDB - Análise Detalhada"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import tmdb
from dashboard.components import charts, sidebar

# ==================== SIDEBAR ====================
sidebar.render_sidebar_header()
year_range, top_n = sidebar.render_tmdb_filters()
sidebar.render_sidebar_footer()

# ==================== HEADER ====================
st.title("📊 TMDB - Análise de Metadados")
st.markdown("**Dados:** Informações completas de filmes")
st.markdown("---")

# ==================== MOSTRAR FILTROS ATIVOS NO TOPO ====================
min_year, max_year = tmdb.get_year_range()

active_filters = []
if year_range != (min_year, max_year):
    active_filters.append(f"📅 {year_range[0]}-{year_range[1]}")
if top_n != 10:
    active_filters.append(f"🏆 Top {top_n}")

if active_filters:
    st.info("**🔍 Filtros Ativos:** " + " • ".join(active_filters))
    st.markdown("---")

# ==================== STATS ====================
st.header("📊 Visão Geral")

stats = tmdb.get_stats()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎬 Total de Filmes", f"{stats['total_movies']:,}")
with col2:
    st.metric("💰 Receita Total", f"${stats['total_revenue']/1e9:.1f}B")
with col3:
    st.metric("💵 Orçamento Total", f"${stats['total_budget']/1e9:.1f}B")

st.markdown("---")

# ==================== TOP REVENUE (COM FILTROS) ====================
st.header(f"💰 Top {top_n} Filmes por Receita")

if year_range != (min_year, max_year):
    st.caption(f"📅 Período: {year_range[0]} - {year_range[1]}")

top_revenue = tmdb.get_top_revenue_movies(
    limit=top_n,
    year_min=year_range[0],
    year_max=year_range[1]
)

if len(top_revenue) > 0:
    # Estatísticas do top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Maior Receita", f"${top_revenue['revenue'].max()/1e6:.1f}M")
    with col2:
        st.metric("📊 Receita Média", f"${top_revenue['revenue'].mean()/1e6:.1f}M")
    with col3:
        st.metric("💵 Orçamento Médio", f"${top_revenue['budget'].mean()/1e6:.1f}M")
    
    fig = charts.create_top_revenue_movies_chart(top_revenue)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Nenhum filme encontrado no período")

st.markdown("---")

# ==================== REVENUE BY YEAR (COM FILTROS) ====================
st.header("📊 Evolução da Receita ao Longo dos Anos")

if year_range != (min_year, max_year):
    st.caption(f"📅 Período: {year_range[0]} - {year_range[1]}")

revenue_by_year = tmdb.get_revenue_by_year(
    year_min=year_range[0],
    year_max=year_range[1]
)

if len(revenue_by_year) > 0:
    # Estatísticas da evolução
    total_revenue = revenue_by_year['total_revenue'].sum()
    avg_revenue_per_year = revenue_by_year['total_revenue'].mean()
    total_movies = revenue_by_year['total_movies'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Receita Total", f"${total_revenue/1e9:.2f}B")
    with col2:
        st.metric("📊 Média por Ano", f"${avg_revenue_per_year/1e9:.2f}B")
    with col3:
        st.metric("🎬 Total de Filmes", f"{total_movies:,}")
    
    fig = charts.create_revenue_by_year_chart(revenue_by_year)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado disponível no período")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("💡 **Dica:** Ajuste o período e o Top N na barra lateral para ver diferentes análises")