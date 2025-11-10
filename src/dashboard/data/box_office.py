"""Queries do Box Office"""

import streamlit as st
import pandas as pd
from settings.db import get_connection

@st.cache_resource
def get_db():
    return get_connection()

@st.cache_data(ttl=3600)
def check_box_office_data():
    """Verifica se há dados Box Office"""
    conn = get_db()
    try:
        query = "SELECT COUNT(*) as count FROM gold_tmdb.fact_box_office"
        df = pd.read_sql(query, conn)
        return int(df.iloc[0]['count']) > 0
    except:
        return False

@st.cache_data(ttl=3600)
def get_year_range():
    """Range de anos Box Office"""
    conn = get_db()
    query = "SELECT MIN(release_year) as min, MAX(release_year) as max FROM gold_tmdb.fact_box_office WHERE release_year IS NOT NULL"
    df = pd.read_sql(query, conn)
    return int(df.iloc[0]['min']), int(df.iloc[0]['max'])

@st.cache_data(ttl=3600)
def get_stats():
    """Estatísticas Box Office"""
    conn = get_db()
    query = """
    SELECT 
        COUNT(*) as total_movies,
        COALESCE(SUM(revenue), 0) as total_revenue,
        COALESCE(SUM(budget), 0) as total_budget,
        COALESCE(SUM(profit), 0) as total_profit,
        COUNT(*) FILTER (WHERE is_profitable = TRUE) as profitable_count,
        COUNT(*) FILTER (WHERE is_blockbuster = TRUE) as blockbuster_count
    FROM gold_tmdb.fact_box_office
    WHERE revenue > 0
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0].to_dict()

@st.cache_data(ttl=3600)
def get_top_profitable_movies(limit=10):
    """Filmes mais lucrativos"""
    conn = get_db()
    query = f"""
    SELECT 
        title,
        release_year,
        revenue,
        budget,
        profit,
        roi
    FROM gold_tmdb.fact_box_office
    WHERE profit IS NOT NULL
    ORDER BY profit DESC
    LIMIT {limit}
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=3600)
def get_profitability_by_year():
    """Taxa de sucesso por ano"""
    conn = get_db()
    query = """
    SELECT 
        release_year as year,
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE is_profitable = TRUE) as profitable,
        ROUND(COUNT(*) FILTER (WHERE is_profitable = TRUE)::NUMERIC / COUNT(*) * 100, 1) as success_rate
    FROM gold_tmdb.fact_box_office
    WHERE release_year IS NOT NULL
    GROUP BY release_year
    HAVING COUNT(*) > 5
    ORDER BY release_year
    """
    return pd.read_sql(query, conn)