"""Queries do TMDB"""

import streamlit as st
import pandas as pd
from settings.db import get_connection

@st.cache_resource
def get_db():
    return get_connection()

@st.cache_data(ttl=3600)
def check_tmdb_data():
    """Verifica se há dados TMDB"""
    conn = get_db()
    try:
        query = "SELECT COUNT(*) as count FROM gold_tmdb.dim_movies_tmdb"
        df = pd.read_sql(query, conn)
        return int(df.iloc[0]['count']) > 0
    except:
        return False

@st.cache_data(ttl=3600)
def get_year_range():
    """Range de anos TMDB"""
    conn = get_db()
    query = "SELECT MIN(release_year) as min, MAX(release_year) as max FROM gold_tmdb.dim_movies_tmdb WHERE release_year IS NOT NULL"
    df = pd.read_sql(query, conn)
    return int(df.iloc[0]['min']), int(df.iloc[0]['max'])

@st.cache_data(ttl=3600)
def get_stats():
    """Estatísticas TMDB"""
    conn = get_db()
    query = """
    SELECT 
        COUNT(*) as total_movies,
        COUNT(*) FILTER (WHERE budget > 0) as with_budget,
        COUNT(*) FILTER (WHERE revenue > 0) as with_revenue,
        COALESCE(SUM(revenue), 0) as total_revenue,
        COALESCE(SUM(budget), 0) as total_budget
    FROM gold_tmdb.dim_movies_tmdb
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0].to_dict()

@st.cache_data(ttl=3600)
def get_top_revenue_movies(limit=10, year_min=None, year_max=None):
    """Top filmes por receita com filtros"""
    conn = get_db()
    
    query = """
    SELECT 
        title,
        release_year,
        revenue,
        budget
    FROM gold_tmdb.dim_movies_tmdb
    WHERE revenue > 0
    """
    
    params = []
    
    if year_min is not None:
        query += " AND release_year >= %s"
        params.append(year_min)
    
    if year_max is not None:
        query += " AND release_year <= %s"
        params.append(year_max)
    
    query += " ORDER BY revenue DESC LIMIT %s"
    params.append(limit)
    
    return pd.read_sql(query, conn, params=params if params else None)

@st.cache_data(ttl=3600)
def get_revenue_by_year(year_min=None, year_max=None):
    """Receita por ano com filtros"""
    conn = get_db()
    
    query = """
    SELECT 
        release_year as year,
        SUM(revenue) as total_revenue,
        COUNT(*) as total_movies
    FROM gold_tmdb.dim_movies_tmdb
    WHERE revenue > 0 AND release_year IS NOT NULL
    """
    
    params = []
    
    if year_min is not None:
        query += " AND release_year >= %s"
        params.append(year_min)
    
    if year_max is not None:
        query += " AND release_year <= %s"
        params.append(year_max)
    
    query += " GROUP BY release_year ORDER BY release_year"
    
    return pd.read_sql(query, conn, params=params if params else None)