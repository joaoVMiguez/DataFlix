from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from settings.db import get_connection

router = APIRouter(
    prefix="/movielens",
    tags=["MovieLens"]
)

@router.get("/top-movies")
def get_top_movies(
    limit: int = Query(10, ge=1, le=100, description="Número de filmes a retornar")
):
    """
    Retorna os top filmes mais bem avaliados do MovieLens.
    
    - **limit**: número de filmes (padrão: 10, máx: 100)
    """
    try:
        conn = get_connection()
        query = f"""
        SELECT 
            movieid,
            title,
            release_year,
            avg_rating,
            total_ratings,
            genres
        FROM gold.vw_top_movies
        LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return {"message": "Nenhum filme encontrado", "data": []}
        
        return {
            "total": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genres")
def get_genre_stats():
    """
    Retorna estatísticas de performance por gênero.
    """
    try:
        conn = get_connection()
        query = """
        SELECT * FROM gold.vw_genre_performance
        ORDER BY total_movies DESC
        """
        df = pd.read_sql(query, conn)
        
        return {
            "total_genres": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies-by-decade")
def get_movies_by_decade():
    """
    Retorna estatísticas de filmes agrupados por década.
    """
    try:
        conn = get_connection()
        query = """
        SELECT * FROM gold.vw_movies_by_decade
        ORDER BY decade
        """
        df = pd.read_sql(query, conn)
        
        return {
            "total_decades": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
def search_movies(
    title: Optional[str] = Query(None, description="Buscar por título"),
    genre: Optional[str] = Query(None, description="Filtrar por gênero"),
    year_min: Optional[int] = Query(None, ge=1900, description="Ano mínimo"),
    year_max: Optional[int] = Query(None, le=2024, description="Ano máximo"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Rating mínimo"),
    limit: int = Query(50, ge=1, le=500, description="Limite de resultados")
):
    """
    Busca filmes com filtros avançados.
    """
    try:
        conn = get_connection()
        
        query = """
        SELECT 
            m.movieid,
            m.title,
            m.release_year,
            m.avg_rating,
            m.total_ratings,
            STRING_AGG(g.genre_name, ', ' ORDER BY g.genre_name) as genres
        FROM gold.dim_movies m
        LEFT JOIN gold.fact_movie_genres fmg ON m.movieid = fmg.movieid
        LEFT JOIN gold.dim_genres g ON fmg.genre_id = g.genre_id
        WHERE 1=1
        """
        
        params = []
        
        if title:
            query += " AND LOWER(m.title) LIKE LOWER(%s)"
            params.append(f"%{title}%")
        
        if year_min:
            query += " AND m.release_year >= %s"
            params.append(year_min)
        
        if year_max:
            query += " AND m.release_year <= %s"
            params.append(year_max)
        
        if rating_min:
            query += " AND m.avg_rating >= %s"
            params.append(rating_min)
        
        query += """
        GROUP BY m.movieid, m.title, m.release_year, m.avg_rating, m.total_ratings
        """
        
        if genre:
            query += " HAVING STRING_AGG(g.genre_name, ', ' ORDER BY g.genre_name) LIKE %s"
            params.append(f"%{genre}%")
        
        query += f" ORDER BY m.total_ratings DESC LIMIT {limit}"
        
        df = pd.read_sql(query, conn, params=params)
        
        return {
            "total": len(df),
            "filters": {
                "title": title,
                "genre": genre,
                "year_range": [year_min, year_max],
                "rating_min": rating_min
            },
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_overall_stats():
    """
    Retorna estatísticas gerais do catálogo MovieLens.
    """
    try:
        conn = get_connection()
        query = """
        SELECT 
            COUNT(*) as total_movies,
            COALESCE(SUM(total_ratings), 0) as total_ratings,
            COALESCE(
                ROUND(
                    CASE
                        WHEN SUM(total_ratings) > 0
                        THEN (SUM(avg_rating * total_ratings) / SUM(total_ratings))::numeric
                        ELSE 0
                    END,
                    2
                ),
                0
            ) as overall_avg_rating,
            COUNT(DISTINCT CASE WHEN total_ratings > 0 THEN movieid END) as rated_movies
        FROM gold.dim_movies
        WHERE avg_rating IS NOT NULL AND total_ratings > 0
        """
        df = pd.read_sql(query, conn)
        result = df.iloc[0].to_dict()
        
        return {
            "total_movies": int(result['total_movies']),
            "total_ratings": int(result['total_ratings']),
            "overall_avg_rating": float(result['overall_avg_rating']),
            "rated_movies": int(result['rated_movies'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))