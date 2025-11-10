"""Queries do MovieLens"""

import streamlit as st
import pandas as pd
from settings.db import get_connection

@st.cache_resource
def get_db():
    return get_connection()

@st.cache_data(ttl=3600)
def get_year_range():
    """Range de anos"""
    conn = get_db()
    query = "SELECT MIN(release_year) as min, MAX(release_year) as max FROM gold.dim_movies WHERE release_year IS NOT NULL"
    df = pd.read_sql(query, conn)
    return int(df.iloc[0]['min']), int(df.iloc[0]['max'])

@st.cache_data(ttl=3600)
def get_stats():
    """Estatísticas gerais"""
    conn = get_db()
    query = """
    SELECT 
        COUNT(DISTINCT m.movieid) as total_movies,
        SUM(r.total_ratings) as total_ratings,
        ROUND(AVG(r.avg_rating)::numeric, 2) as avg_rating
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0].to_dict()

@st.cache_data(ttl=3600)
def get_movie_details(movie_title):
    """Busca detalhes de um filme específico"""
    conn = get_db()
    
    query = """
    SELECT 
        m.movieid,
        m.title,
        m.release_year,
        STRING_AGG(DISTINCT g.genre_name, ' | ' ORDER BY g.genre_name) as genres,
        COALESCE(r.avg_rating, 0) as avg_rating,
        COALESCE(r.total_ratings, 0) as num_ratings
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_genres mg ON m.movieid = mg.movieid
    LEFT JOIN gold.dim_genres g ON mg.genre_id = g.genre_id
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE LOWER(m.title) LIKE LOWER(%s)
    GROUP BY m.movieid, m.title, m.release_year, r.avg_rating, r.total_ratings
    ORDER BY 
        CASE 
            WHEN r.total_ratings IS NULL THEN 0
            ELSE r.avg_rating * LOG(r.total_ratings + 1)
        END DESC,
        r.total_ratings DESC NULLS LAST
    LIMIT 20
    """
    
    return pd.read_sql(query, conn, params=[f"%{movie_title}%"])

@st.cache_data(ttl=3600)
def get_movie_by_id(movie_id):
    """Busca filme pelo ID"""
    conn = get_db()
    
    query = """
    SELECT 
        m.movieid,
        m.title,
        m.release_year,
        STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) as genres,
        COALESCE(r.avg_rating, 0) as avg_rating,
        COALESCE(r.total_ratings, 0) as num_ratings
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_genres mg ON m.movieid = mg.movieid
    LEFT JOIN gold.dim_genres g ON mg.genre_id = g.genre_id
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE m.movieid = %s
    GROUP BY m.movieid, m.title, m.release_year, r.avg_rating, r.total_ratings
    """
    
    df = pd.read_sql(query, conn, params=[movie_id])
    return df.iloc[0] if len(df) > 0 else None

@st.cache_data(ttl=3600)
def get_top_movies(limit=10, year_min=None, year_max=None):
    """Top filmes com filtros opcionais"""
    conn = get_db()
    
    query = """
    SELECT 
        m.title,
        m.release_year,
        r.avg_rating,
        r.total_ratings as num_ratings
    FROM gold.dim_movies m
    INNER JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE r.total_ratings >= 50
    """
    
    params = []
    
    if year_min is not None:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max is not None:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    query += " ORDER BY r.avg_rating DESC, r.total_ratings DESC LIMIT %s"
    params.append(limit)
    
    return pd.read_sql(query, conn, params=params if params else None)

@st.cache_data(ttl=3600)
def get_genres():
    """Lista de gêneros"""
    conn = get_db()
    query = "SELECT DISTINCT genre_name FROM gold.dim_genres ORDER BY genre_name"
    df = pd.read_sql(query, conn)
    return df['genre_name'].tolist()

@st.cache_data(ttl=3600)
def get_movies_by_decade(year_min=None, year_max=None):
    """Filmes agrupados por década com filtros"""
    conn = get_db()
    
    query = """
    SELECT 
        (release_year / 10) * 10 as decade,
        COUNT(DISTINCT m.movieid) as total_movies,
        ROUND(AVG(r.avg_rating)::numeric, 2) as avg_rating
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE release_year IS NOT NULL
    """
    
    params = []
    
    if year_min is not None:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max is not None:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    query += " GROUP BY decade ORDER BY decade"
    
    return pd.read_sql(query, conn, params=params if params else None)

@st.cache_data(ttl=3600)
def get_genre_stats(year_min=None, year_max=None):
    """Estatísticas por gênero com filtros"""
    conn = get_db()
    
    query = """
    SELECT 
        g.genre_name as genre,
        COUNT(DISTINCT mg.movieid) as total_movies,
        ROUND(AVG(r.avg_rating)::numeric, 2) as avg_rating
    FROM gold.dim_genres g
    INNER JOIN gold.fact_movie_genres mg ON g.genre_id = mg.genre_id
    LEFT JOIN gold.fact_movie_ratings r ON mg.movieid = r.movieid
    LEFT JOIN gold.dim_movies m ON mg.movieid = m.movieid
    WHERE 1=1
    """
    
    params = []
    
    if year_min is not None:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max is not None:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    query += """
    GROUP BY g.genre_name
    HAVING COUNT(DISTINCT mg.movieid) > 0
    ORDER BY total_movies DESC
    """
    
    return pd.read_sql(query, conn, params=params if params else None)

@st.cache_data(ttl=3600)
def search_movies(search_term="", genre="", year_min=None, year_max=None, rating_min=0, limit=50, offset=0):
    """Busca filmes com ordenação melhorada e paginação"""
    conn = get_db()
    
    query = """
    SELECT 
        m.movieid,
        m.title,
        m.release_year,
        STRING_AGG(DISTINCT g.genre_name, ' | ' ORDER BY g.genre_name) as genres,
        COALESCE(r.avg_rating, 0) as avg_rating,
        COALESCE(r.total_ratings, 0) as num_ratings
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_genres mg ON m.movieid = mg.movieid
    LEFT JOIN gold.dim_genres g ON mg.genre_id = g.genre_id
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE 1=1
    """
    
    params = []
    
    if search_term:
        query += " AND LOWER(m.title) LIKE LOWER(%s)"
        params.append(f"%{search_term}%")
    
    if genre:
        query += " AND m.movieid IN (SELECT mg2.movieid FROM gold.fact_movie_genres mg2 INNER JOIN gold.dim_genres g2 ON mg2.genre_id = g2.genre_id WHERE g2.genre_name = %s)"
        params.append(genre)
    
    if year_min:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    if rating_min > 0:
        query += " AND r.avg_rating >= %s"
        params.append(rating_min)
    
    query += " GROUP BY m.movieid, m.title, m.release_year, r.avg_rating, r.total_ratings"
    query += """
    ORDER BY 
        CASE 
            WHEN r.total_ratings IS NULL THEN 0
            ELSE r.avg_rating * LOG(r.total_ratings + 1)
        END DESC,
        r.total_ratings DESC NULLS LAST,
        m.release_year DESC
    """
    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return pd.read_sql(query, conn, params=params if params else None)

@st.cache_data(ttl=3600)
def count_search_results(search_term="", genre="", year_min=None, year_max=None, rating_min=0):
    """Conta total de resultados para paginação"""
    conn = get_db()
    
    query = """
    SELECT COUNT(DISTINCT m.movieid) as total
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_genres mg ON m.movieid = mg.movieid
    LEFT JOIN gold.dim_genres g ON mg.genre_id = g.genre_id
    LEFT JOIN gold.fact_movie_ratings r ON m.movieid = r.movieid
    WHERE 1=1
    """
    
    params = []
    
    if search_term:
        query += " AND LOWER(m.title) LIKE LOWER(%s)"
        params.append(f"%{search_term}%")
    
    if genre:
        query += " AND m.movieid IN (SELECT mg2.movieid FROM gold.fact_movie_genres mg2 INNER JOIN gold.dim_genres g2 ON mg2.genre_id = g2.genre_id WHERE g2.genre_name = %s)"
        params.append(genre)
    
    if year_min:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    if rating_min > 0:
        query += " AND r.avg_rating >= %s"
        params.append(rating_min)
    
    df = pd.read_sql(query, conn, params=params if params else None)
    return int(df.iloc[0]['total'])
    