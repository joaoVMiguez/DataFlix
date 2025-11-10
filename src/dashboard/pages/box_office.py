"""Página Box Office - Análise Detalhada"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import box_office
from dashboard.components import charts, sidebar

# ==================== SIDEBAR ====================
sidebar.render_sidebar_header()
year_range, min_revenue = sidebar.render_box_office_filters()
sidebar.render_sidebar_footer()

# ==================== HEADER ====================
st.title("💰 Box Office - Análise Financeira")
st.markdown("**Dados:** Performance de bilheteria")
st.markdown("---")

# ==================== MOSTRAR FILTROS ATIVOS NO TOPO ====================
min_year, max_year = box_office.get_year_range()

active_filters = []
if year_range != (min_year, max_year):
    active_filters.append(f"📅 {year_range[0]}-{year_range[1]}")
if min_revenue > 0:
    active_filters.append(f"💰 Receita ≥ ${min_revenue/1e6:.0f}M")

if active_filters:
    st.info("**🔍 Filtros Ativos:** " + " • ".join(active_filters))
    st.markdown("---")

# ==================== STATS ====================
st.header("📊 Visão Geral")

stats = box_office.get_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎬 Filmes", f"{stats['total_movies']:,}")
with col2:
    st.metric("💎 Lucro", f"${stats['total_profit']/1e9:.1f}B")
with col3:
    st.metric("✅ Lucrativos", f"{stats['profitable_count']:,}")
with col4:
    st.metric("🌟 Blockbusters", f"{stats['blockbuster_count']:,}")

st.markdown("---")

# ==================== TOP PROFITABLE ====================
st.header("💎 Top 10 Filmes Mais Lucrativos")

if year_range != (min_year, max_year):
    st.caption(f"📅 Período: {year_range[0]} - {year_range[1]}")

top_profitable = box_office.get_top_profitable_movies(10)

if len(top_profitable) > 0:
    # Estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Maior Lucro", f"${top_profitable['profit'].max()/1e6:.1f}M")
    with col2:
        st.metric("📊 Lucro Médio", f"${top_profitable['profit'].mean()/1e6:.1f}M")
    with col3:
        st.metric("📈 ROI Médio", f"{top_profitable['roi'].mean():.1f}%")
    
    fig = charts.create_top_profitable_movies_chart(top_profitable)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Nenhum filme encontrado")

st.markdown("---")

# ==================== SUCCESS RATE ====================
st.header("📈 Taxa de Sucesso por Ano")
st.caption("Percentual de filmes lucrativos")

if year_range != (min_year, max_year):
    st.caption(f"📅 Período: {year_range[0]} - {year_range[1]}")

profitability = box_office.get_profitability_by_year()

if len(profitability) > 0:
    avg_success_rate = profitability['success_rate'].mean()
    st.metric("📊 Taxa Média de Sucesso", f"{avg_success_rate:.1f}%")
    
    fig = charts.create_success_rate_chart(profitability)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado disponível")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("💡 **Dica:** Use os filtros na barra lateral para análises específicas")