from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from settings.db import get_connection

router = APIRouter(
    prefix="/tmdb",
    tags=["TMDB"]
)

@router.get("/box-office")
def get_box_office(
    limit: int = Query(20, ge=1, le=100, description="Número de filmes")
):
    """
    Retorna dados de bilheteria (receita, orçamento, ROI).
    """
    try:
        conn = get_connection()
        query = f"""
        SELECT 
            movielens_id,
            title,
            release_year,
            budget,
            revenue,
            profit,
            roi,
            payback_ratio,
            budget_category,
            revenue_category,
            roi_category,
            is_profitable,
            is_blockbuster
        FROM gold_tmdb.fact_box_office
        WHERE revenue > 0
        ORDER BY revenue DESC
        LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
        
        return {
            "total": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/studio-performance")
def get_studio_performance(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Retorna performance dos estúdios de produção.
    """
    try:
        conn = get_connection()
        query = f"""
        SELECT *
        FROM gold_tmdb.fact_studio_performance
        ORDER BY total_revenue DESC
        LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
        
        return {
            "total_studios": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/country-performance")
def get_country_performance():
    """
    Retorna performance por país de produção.
    """
    try:
        conn = get_connection()
        query = """
        SELECT 
            country_code,
            country_name,
            total_movies,
            avg_budget,
            avg_revenue,
            avg_roi,
            total_profit,
            top_genre,
            most_prolific_studio
        FROM gold_tmdb.fact_country_performance
        ORDER BY avg_revenue DESC
        """
        df = pd.read_sql(query, conn)
        
        return {
            "total_countries": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies")
def get_tmdb_movies(
    limit: int = Query(50, ge=1, le=500),
    min_budget: Optional[float] = Query(None, ge=0),
    min_revenue: Optional[float] = Query(None, ge=0),
    year: Optional[int] = Query(None, ge=1900, le=2024)
):
    """
    Busca filmes do TMDB com filtros.
    """
    try:
        conn = get_connection()
        
        query = """
        SELECT *
        FROM gold_tmdb.dim_movies_tmdb
        WHERE 1=1
        """
        
        params = []
        
        if min_budget:
            query += " AND budget >= %s"
            params.append(min_budget)
        
        if min_revenue:
            query += " AND revenue >= %s"
            params.append(min_revenue)
        
        if year:
            query += " AND release_year = %s"
            params.append(year)
        
        query += f" ORDER BY revenue DESC LIMIT {limit}"
        
        df = pd.read_sql(query, conn, params=params)
        
        return {
            "total": len(df),
            "filters": {
                "min_budget": min_budget,
                "min_revenue": min_revenue,
                "year": year
            },
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_tmdb_stats():
    """
    Estatísticas gerais do catálogo TMDB.
    """
    try:
        conn = get_connection()
        query = """
        SELECT 
            COUNT(*) as total_movies,
            SUM(budget) as total_budget,
            SUM(revenue) as total_revenue,
            AVG(vote_average) as avg_rating,
            SUM(vote_count) as total_votes
        FROM gold_tmdb.dim_movies_tmdb
        WHERE budget > 0 AND revenue > 0
        """
        df = pd.read_sql(query, conn)
        result = df.iloc[0].to_dict()
        
        return {
            "total_movies": int(result['total_movies']),
            "total_budget": float(result['total_budget']),
            "total_revenue": float(result['total_revenue']),
            "avg_rating": float(result['avg_rating']),
            "total_votes": int(result['total_votes'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))