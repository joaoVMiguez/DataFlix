"""Página Box Office - Estilo Protótipo Moderno"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import box_office
from dashboard.components import charts
from dashboard.components import navigation

# ==================== NAVEGAÇÃO ====================
navigation.render_navigation("box_office")

# ==================== HEADER ====================
st.markdown("""
<div style='margin-bottom: 1rem;'>
    <h1 style='font-size: 2.5rem; font-weight: 800; margin: 0;'>Box Office Analytics</h1>
    <p style='color: #666; margin: 0.5rem 0 0 0;'>Análise de lucratividade e performance de bilheteria</p>
</div>
""", unsafe_allow_html=True)

# ==================== STATS CARDS ====================
stats = box_office.get_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue_bi = stats['total_revenue'] / 1e9
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Receita Total</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>US$ {revenue_bi:.1f} bi</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>💰</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    profit_bi = stats['total_profit'] / 1e9
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Lucro Total</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>US$ {profit_bi:.1f} bi</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>📈</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_roi = (stats['total_profit'] / stats['total_budget'] * 100) if stats['total_budget'] > 0 else 0
    st.markdown(f"""
    <div style='background: white; border: 2px solid #e5e7eb;
                border-radius: 12px; padding: 1.5rem;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; color: #666; font-size: 0.85rem;'>ROI Médio</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700; color: #111;'>{avg_roi:.0f}%</h2>
            </div>
            <div style='background: #f3f4f6; padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>🎯</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Blockbusters</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>{stats['blockbuster_count']}</h2>
                <p style='margin: 0.25rem 0 0 0; font-size: 0.75rem; opacity: 0.8;'>Receita > $200M</p>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>🌟</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== TOP FILMES ====================
st.markdown("""
<div style='margin-bottom: 1rem;'>
    <h3 style='margin: 0; font-size: 1.3rem; font-weight: 700;'>Filmes Mais Lucrativos</h3>
</div>
""", unsafe_allow_html=True)

top_profitable = box_office.get_top_profitable_movies(5)

if len(top_profitable) > 0:
    # Criar tabela estilo protótipo
    table_data = []
    for idx, row in top_profitable.iterrows():
        revenue_bi = row['revenue'] / 1e9
        budget_mi = row['budget'] / 1e6
        profit_bi = row['profit'] / 1e9 if row['profit'] else 0
        roi = row['roi'] if row['roi'] else 0
        is_blockbuster = row['revenue'] > 200000000
        
        table_data.append({
            '#': idx + 1,
            'Título': row['title'],
            'Ano': int(row['release_year']) if row['release_year'] else 'N/A',
            'Receita': f"US$ {revenue_bi:.1f} bi",
            'Orçamento': f"US$ {budget_mi:.0f} mi",
            'Lucro': f"US$ {profit_bi:.1f} bi",
            'ROI': f"+{roi:.0f}%",
            'Status': '⭐ Blockbuster' if is_blockbuster else ''
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
            'ROI': st.column_config.TextColumn('ROI', width="small"),
            'Status': st.column_config.TextColumn('Status', width="medium")
        },
        hide_index=True,
        use_container_width=True,
        height=250
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== INDICADORES ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e5e7eb;'>
        <h4 style='margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center;'>
            <span style='color: #11998e; margin-right: 0.5rem;'>📈</span>
            Indicadores de Sucesso
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    success_rate = (stats['profitable_count'] / stats['total_movies'] * 100) if stats['total_movies'] > 0 else 0
    
    st.markdown(f"""
    <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb; margin-top: 1rem;'>
        <p style='margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;'>Taxa de Lucratividade</p>
        <div style='background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;'>
            <div style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                        width: {success_rate}%; height: 100%;'></div>
        </div>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 700;'>{success_rate:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb; margin-top: 1rem;'>
        <p style='margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;'>Média de Blockbusters</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 700;'>5 de 5</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e5e7eb;'>
        <h4 style='margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center;'>
            <span style='color: #667eea; margin-right: 0.5rem;'>🎯</span>
            Performance Financeira
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    if len(top_profitable) > 0:
        max_profit = top_profitable['profit'].max() / 1e9
        best_roi = top_profitable['roi'].max()
        avg_profit = top_profitable['profit'].mean() / 1e9
        
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb; margin-top: 1rem;'>
            <p style='margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;'>Maior Lucro</p>
            <p style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #11998e;'>US$ {max_profit:.1f} bi</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb; margin-top: 1rem;'>
            <p style='margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;'>Melhor ROI</p>
            <p style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #11998e;'>{best_roi:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem; border: 1px solid #e5e7eb; margin-top: 1rem;'>
            <p style='margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;'>Lucro Médio</p>
            <p style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #667eea;'>US$ {avg_profit:.1f} bi</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== GRÁFICOS ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💎 Top 10 Mais Lucrativos")
    top_10 = box_office.get_top_profitable_movies(10)
    if len(top_10) > 0:
        st.plotly_chart(charts.create_top_profitable_movies_chart(top_10), use_container_width=True)

with col2:
    st.markdown("### 📈 Taxa de Sucesso por Ano")
    profitability = box_office.get_profitability_by_year()
    if len(profitability) > 0:
        st.plotly_chart(charts.create_success_rate_chart(profitability), use_container_width=True)