import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from config.db import get_connection

def aggregate_movie_ratings():
    """
    Agrega estatísticas de ratings por filme
    Retorna DataFrame pronto para gold.fact_movie_ratings
    """
    print("  📊 Agregando ratings por filme...")
    
    conn = get_connection()
    
    query = """
    SELECT 
        movieid,
        COUNT(*) as total_ratings,
        ROUND(AVG(rating)::numeric, 2) as avg_rating,
        MIN(rating) as min_rating,
        MAX(rating) as max_rating,
        ROUND(STDDEV(rating)::numeric, 2) as stddev_rating,
        COUNT(DISTINCT userid) as total_users
    FROM silver.ratings_silver
    GROUP BY movieid
    ORDER BY movieid
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} filmes com ratings agregados")
    return df


def aggregate_ratings_by_year():
    """
    Agrega ratings por ano (temporal)
    Retorna DataFrame pronto para gold.fact_ratings_by_year
    """
    print("  📊 Agregando ratings por ano...")
    
    conn = get_connection()
    
    query = """
    SELECT 
        EXTRACT(YEAR FROM TO_TIMESTAMP(timestamp))::int as rating_year,
        COUNT(*) as total_ratings,
        ROUND(AVG(rating)::numeric, 2) as avg_rating,
        COUNT(DISTINCT userid) as active_users,
        COUNT(DISTINCT movieid) as movies_rated
    FROM silver.ratings_silver
    GROUP BY rating_year
    ORDER BY rating_year
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df)} anos processados")
    return df


def enrich_movies_dimension():
    """
    Enriquece dimensão de filmes com métricas agregadas
    OTIMIZADO: Queries separadas ao invés de JOINs gigantes
    """
    print("  📊 Enriquecendo dimensão de filmes...")
    
    conn = get_connection()
    
    # 1. Busca filmes base
    print("    → Buscando filmes base...")
    query_movies = """
    SELECT 
        m.movieid,
        m.title,
        m.release_year,
        l.imdbid,
        l.tmdbid
    FROM silver.movies_silver m
    LEFT JOIN silver.links_silver l ON m.movieid = l.movieid
    ORDER BY m.movieid
    """
    df_movies = pd.read_sql(query_movies, conn)
    
    # 2. Busca métricas de ratings (agregado)
    print("    → Calculando métricas de ratings...")
    query_ratings = """
    SELECT 
        movieid,
        ROUND(AVG(rating)::numeric, 2) as avg_rating,
        COUNT(*) as total_ratings,
        COUNT(DISTINCT userid) as total_users
    FROM silver.ratings_silver
    GROUP BY movieid
    """
    df_ratings = pd.read_sql(query_ratings, conn)
    
    # 3. Busca total de tags
    print("    → Calculando total de tags...")
    query_tags = """
    SELECT 
        movieid,
        COUNT(DISTINCT tag) as total_tags
    FROM silver.tags_silver
    GROUP BY movieid
    """
    df_tags = pd.read_sql(query_tags, conn)
    
    conn.close()
    
    # 4. Merge tudo (no Python, mais rápido que SQL)
    print("    → Consolidando dados...")
    df = df_movies.merge(df_ratings, on='movieid', how='left')
    df = df.merge(df_tags, on='movieid', how='left')
    
    # Trata valores nulos
    df['total_ratings'] = df['total_ratings'].fillna(0).astype(int)
    df['total_users'] = df['total_users'].fillna(0).astype(int)
    df['total_tags'] = df['total_tags'].fillna(0).astype(int)
    
    print(f"  ✓ {len(df):,} filmes enriquecidos")
    return df


def aggregate_genres():
    """
    Agrega estatísticas por gênero
    Retorna DataFrame pronto para gold.dim_genres
    """
    print("  📊 Agregando estatísticas por gênero...")
    
    conn = get_connection()
    
    query = """
    SELECT 
        g.genre_id,
        g.genre_name,
        COUNT(DISTINCT mg.movieid) as total_movies,
        COUNT(r.rating) as total_ratings,
        ROUND(AVG(r.rating)::numeric, 2) as avg_rating
    FROM silver.genres_silver g
    LEFT JOIN silver.movie_genres_silver mg ON g.genre_id = mg.genre_id
    LEFT JOIN silver.ratings_silver r ON mg.movieid = r.movieid
    GROUP BY g.genre_id, g.genre_name
    ORDER BY g.genre_name
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Trata valores nulos
    df['total_movies'] = df['total_movies'].fillna(0).astype(int)
    df['total_ratings'] = df['total_ratings'].fillna(0).astype(int)
    
    print(f"  ✓ {len(df)} gêneros processados")
    return df


def get_movie_genres_relationships():
    """
    Busca relacionamentos filme-gênero
    Retorna DataFrame pronto para gold.fact_movie_genres
    """
    print("  📊 Buscando relacionamentos filme-gênero...")
    
    conn = get_connection()
    
    query = """
    SELECT 
        movieid,
        genre_id
    FROM silver.movie_genres_silver
    ORDER BY movieid, genre_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} relacionamentos")
    return df