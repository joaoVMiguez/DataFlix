"""Página TMDB - Estilo Protótipo Moderno"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import tmdb
from dashboard.components import charts
from dashboard.components import navigation

# ==================== NAVEGAÇÃO ====================
navigation.render_navigation("tmdb")

# ==================== HEADER ====================
st.markdown("""
<div style='margin-bottom: 1rem;'>
    <h1 style='font-size: 2.5rem; font-weight: 800; margin: 0;'>TMDB Analytics</h1>
    <p style='color: #666; margin: 0.5rem 0 0 0;'>Análise de receita, orçamento e performance financeira</p>
</div>
""", unsafe_allow_html=True)

# ==================== STATS CARDS ====================
stats = tmdb.get_stats()

col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

with col1:
    st.markdown(f"""
    <div style='background: white; border: 2px solid #e5e7eb;
                border-radius: 12px; padding: 1.5rem;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; color: #666; font-size: 0.85rem;'>Total de Filmes</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700; color: #111;'>{stats['total_movies']:,}</h2>
            </div>
            <div style='background: #f3f4f6; padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>🎬</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    revenue_bi = stats['total_revenue'] / 1e9
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Receita Total (Top 5)</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>US$ {revenue_bi:.1f} bi</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>💰</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    budget_bi = stats['total_budget'] / 1e9
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Orçamento Total (Top 5)</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>US$ {budget_bi:.1f} bi</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>📊</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    profit_bi = (stats['total_revenue'] - stats['total_budget']) / 1e9
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Lucro (Top 5)</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>US$ {profit_bi:.1f} bi</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>📈</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== TOP FILMES ====================
st.markdown("""
<div style='margin-bottom: 1rem;'>
    <h3 style='margin: 0; font-size: 1.3rem; font-weight: 700;'>Top 5 Filmes por Receita</h3>
</div>
""", unsafe_allow_html=True)

min_year, max_year = tmdb.get_year_range()
top_revenue = tmdb.get_top_revenue_movies(limit=5, year_min=min_year, year_max=max_year)

if len(top_revenue) > 0:
    # Criar tabela estilo protótipo
    table_data = []
    for idx, row in top_revenue.iterrows():
        revenue_bi = row['revenue'] / 1e9
        budget_mi = row['budget'] / 1e6
        profit_bi = (row['revenue'] - row['budget']) / 1e9
        roi = ((row['revenue'] - row['budget']) / row['budget'] * 100) if row['budget'] > 0 else 0
        
        table_data.append({
            '#': idx + 1,
            'Título': row['title'],
            'Ano': int(row['release_year']) if row['release_year'] else 'N/A',
            'Receita': f"US$ {revenue_bi:.1f} bi",
            'Orçamento': f"US$ {budget_mi:.0f} mi",
            'Lucro': f"US$ {profit_bi:.1f} bi",
            'ROI': f"+{roi:.0f}%"
        })
    
    import pandas as pd
    df_display = pd.DataFrame(table_data)
    
    st.dataframe(
        df_display,
        column_config={
            '#': st.column_config.NumberColumn('#', width="small"),
            'Título': st.column_config.TextColumn('Título', width="large"),
            'Ano': st.column_config.TextColumn('Ano', width="small"),
            'Receita': st.column_config.TextColumn('Receita', width="medium"),
            'Orçamento': st.column_config.TextColumn('Orçamento', width="medium"),
            'Lucro': st.column_config.TextColumn('Lucro', width="medium"),
            'ROI': st.column_config.TextColumn('ROI', width="small")
        },
        hide_index=True,
        use_container_width=True,
        height=250
    )
    
    # Métricas abaixo da tabela
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_revenue = top_revenue['revenue'].mean() / 1e9
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb;'>
            <p style='margin: 0; color: #ff6b6b; font-size: 0.85rem; font-weight: 600;'>🔴 Receita Média</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>US$ {avg_revenue:.1f} bi</p>
            <p style='margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #666;'>Por filme (Top 5)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_budget = top_revenue['budget'].mean() / 1e6
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb;'>
            <p style='margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 600;'>🔵 Orçamento Médio</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>US$ {avg_budget:.0f} mi</p>
            <p style='margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #666;'>Por filme (Top 5)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_roi = ((top_revenue['revenue'].mean() - top_revenue['budget'].mean()) / top_revenue['budget'].mean() * 100)
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb;'>
            <p style='margin: 0; color: #11998e; font-size: 0.85rem; font-weight: 600;'>🟢 ROI Médio</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>{avg_roi:.0f}%</p>
            <p style='margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #666;'>Retorno sobre investimento</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== GRÁFICOS ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Top 10 por Receita")
    top_10 = tmdb.get_top_revenue_movies(limit=10, year_min=min_year, year_max=max_year)
    if len(top_10) > 0:
        st.plotly_chart(charts.create_top_revenue_movies_chart(top_10), use_container_width=True)

with col2:
    st.markdown("### 📈 Evolução da Receita")
    revenue_by_year = tmdb.get_revenue_by_year(year_min=min_year, year_max=max_year)
    if len(revenue_by_year) > 0:
        st.plotly_chart(charts.create_revenue_by_year_chart(revenue_by_year), use_container_width=True)