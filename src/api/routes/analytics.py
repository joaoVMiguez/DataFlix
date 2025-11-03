from fastapi import APIRouter, HTTPException
import pandas as pd
from settings.db import get_connection

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/compare-datasets")
def compare_datasets():
    """
    Compara estatísticas entre MovieLens e TMDB.
    """
    try:
        conn = get_connection()
        
        # MovieLens stats
        ml_query = """
        SELECT 
            COUNT(*) as total_movies,
            SUM(total_ratings) as total_ratings,
            AVG(avg_rating) as avg_rating
        FROM gold.dim_movies
        WHERE total_ratings > 0
        """
        ml_stats = pd.read_sql(ml_query, conn).iloc[0].to_dict()
        
        # TMDB stats
        tmdb_query = """
        SELECT 
            COUNT(*) as total_movies,
            SUM(revenue) as total_revenue,
            AVG(vote_average) as avg_rating
        FROM gold_tmdb.dim_movies_tmdb
        WHERE revenue > 0
        """
        tmdb_stats = pd.read_sql(tmdb_query, conn).iloc[0].to_dict()
        
        return {
            "movielens": {
                "total_movies": int(ml_stats['total_movies']),
                "total_ratings": int(ml_stats['total_ratings']),
                "avg_rating": float(ml_stats['avg_rating'])
            },
            "tmdb": {
                "total_movies": int(tmdb_stats['total_movies']),
                "total_revenue": float(tmdb_stats['total_revenue']),
                "avg_rating": float(tmdb_stats['avg_rating'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-genres-comparison")
def compare_top_genres():
    """
    Compara top gêneros entre as duas fontes.
    """
    try:
        conn = get_connection()
        
        # MovieLens
        ml_query = """
        SELECT genre_name, total_movies, avg_rating
        FROM gold.vw_genre_performance
        ORDER BY total_movies DESC
        LIMIT 10
        """
        ml_genres = pd.read_sql(ml_query, conn)
        
        return {
            "movielens_top_genres": ml_genres.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))