"""
MovieLens data repository
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class MovieLensRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_stats(self) -> Dict[str, Any]:
        """Get general MovieLens statistics"""
        query = text("""
            SELECT 
                COUNT(DISTINCT dm.movieid) as total_movies,
                SUM(fmr.total_users) as total_users,
                SUM(fmr.total_ratings) as total_ratings,
                AVG(fmr.avg_rating) as avg_rating
            FROM gold.dim_movies dm
            LEFT JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
        """)
        result = self.db.execute(query).fetchone()
        
        total_ratings = result.total_ratings or 0
        
        return {
            "total_movies": result.total_movies or 0,
            "total_ratings": f"{total_ratings / 1_000_000:.1f}M+" if total_ratings >= 1_000_000 else str(total_ratings),
            "avg_rating": round(result.avg_rating or 0, 2),
            "active_users": result.total_users or 0
        }
    
    def get_top_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top rated movies with minimum ratings threshold"""
        query = text("""
            SELECT 
                dm.movieid,
                dm.title,
                dm.release_year,
                fmr.avg_rating,
                fmr.total_ratings,
                STRING_AGG(DISTINCT dg.genre_name, ', ' ORDER BY dg.genre_name) as genres_str
            FROM gold.dim_movies dm
            JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
            LEFT JOIN gold.fact_movie_genres fmg ON dm.movieid = fmg.movieid
            LEFT JOIN gold.dim_genres dg ON fmg.genre_id = dg.genre_id
            WHERE fmr.total_ratings >= 100
            GROUP BY dm.movieid, dm.title, dm.release_year, fmr.avg_rating, fmr.total_ratings
            ORDER BY fmr.avg_rating DESC, fmr.total_ratings DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "title": r.title,
                "release_year": r.release_year,
                "avg_rating": round(r.avg_rating, 2),
                "total_ratings": r.total_ratings,
                "genres": r.genres_str.split(', ') if r.genres_str else []
            }
            for r in results
        ]
    
    def get_genre_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by genre"""
        query = text("""
            SELECT 
                dg.genre_id,
                dg.genre_name,
                COUNT(DISTINCT fmg.movieid) as total_movies,
                COALESCE(SUM(fmr.total_ratings), 0) as total_ratings,
                COALESCE(AVG(fmr.avg_rating), 0) as avg_rating
            FROM gold.dim_genres dg
            JOIN gold.fact_movie_genres fmg ON dg.genre_id = fmg.genre_id
            LEFT JOIN gold.fact_movie_ratings fmr ON fmg.movieid = fmr.movieid
            GROUP BY dg.genre_id, dg.genre_name
            ORDER BY total_movies DESC
        """)
        results = self.db.execute(query).fetchall()
        
        return [
            {
                "genre_id": r.genre_id,
                "genre_name": r.genre_name,
                "total_movies": r.total_movies,
                "total_ratings": r.total_ratings,
                "avg_rating": round(r.avg_rating, 2)
            }
            for r in results
        ]
    
    def search_movies(
        self, 
        query: str, 
        genre: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search movies by title and optional genre"""
        sql = """
            SELECT 
                dm.movieid,
                dm.title,
                dm.release_year,
                STRING_AGG(dg.genre_name, ', ' ORDER BY dg.genre_name) as genres,
                COALESCE(MAX(fmr.avg_rating), 0) as avg_rating,
                COALESCE(MAX(fmr.total_ratings), 0) as total_ratings
            FROM gold.dim_movies dm
            LEFT JOIN gold.fact_movie_genres fmg ON dm.movieid = fmg.movieid
            LEFT JOIN gold.dim_genres dg ON fmg.genre_id = dg.genre_id
            LEFT JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
            WHERE LOWER(dm.title) LIKE LOWER(:query)
        """
        
        params = {"query": f"%{query}%", "limit": limit}
        
        if genre and genre.lower() != "all":
            sql += " AND EXISTS (SELECT 1 FROM gold.fact_movie_genres fmg2 JOIN gold.dim_genres dg2 ON fmg2.genre_id = dg2.genre_id WHERE fmg2.movieid = dm.movieid AND dg2.genre_name = :genre)"
            params["genre"] = genre
        
        sql += """
            GROUP BY dm.movieid, dm.title, dm.release_year
            ORDER BY total_ratings DESC NULLS LAST, avg_rating DESC NULLS LAST
            LIMIT :limit
        """
        
        results = self.db.execute(text(sql), params).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "title": r.title,
                "release_year": r.release_year,
                "genres": r.genres or "",
                "avg_rating": round(r.avg_rating, 2),
                "total_ratings": r.total_ratings
            }
            for r in results
        ]
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by ID"""
        query = text("""
            SELECT 
                dm.movieid,
                dm.title,
                dm.release_year,
                fmr.avg_rating,
                fmr.total_ratings,
                fmr.total_users,
                STRING_AGG(DISTINCT dg.genre_name, ', ' ORDER BY dg.genre_name) as genres_str,
                mt.overview as description,
                mt.poster_path as poster_path
            FROM gold.dim_movies dm
            LEFT JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
            LEFT JOIN gold.fact_movie_genres fmg ON dm.movieid = fmg.movieid
            LEFT JOIN gold.dim_genres dg ON fmg.genre_id = dg.genre_id
            LEFT JOIN silver_tmdb.movies_tmdb mt ON dm.movieid = mt.movielens_id
            WHERE dm.movieid = :movie_id
            GROUP BY dm.movieid, dm.title, dm.release_year, fmr.avg_rating, fmr.total_ratings, fmr.total_users, mt.overview, mt.poster_path
        """)
        result = self.db.execute(query, {"movie_id": movie_id}).fetchone()
        
        if not result:
            return None
        
        return {
            "movieid": result.movieid,
            "title": result.title,
            "release_year": result.release_year,
            "avg_rating": round(result.avg_rating or 0, 2),
            "total_ratings": result.total_ratings or 0,
            "total_users": result.total_users or 0,
            "genres": result.genres_str.split(', ') if result.genres_str else [],
            "description": result.description or "Descrição não disponível para este filme.",
            "poster_path": result.poster_path or None
        }
    
    # ============ PAGINAÇÃO ============
    def get_movies_paginated(
        self, 
        limit: int = 10, 
        offset: int = 0,
        genre: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated movies with total count"""
        
        # Base query
        base_filter = "WHERE fmr.total_ratings >= 100"
        genre_filter = ""
        params = {"limit": limit, "offset": offset}
        
        if genre and genre.lower() != "all":
            genre_filter = """ 
                AND EXISTS (
                    SELECT 1 FROM gold.fact_movie_genres fmg2 
                    JOIN gold.dim_genres dg2 ON fmg2.genre_id = dg2.genre_id 
                    WHERE fmg2.movieid = dm.movieid AND dg2.genre_name = :genre
                )
            """
            params["genre"] = genre
        
        # Count query
        count_sql = f"""
            SELECT COUNT(DISTINCT dm.movieid) as total
            FROM gold.dim_movies dm
            JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
            {base_filter}
            {genre_filter}
        """
        
        # Data query
        data_sql = f"""
            SELECT 
                dm.movieid,
                dm.title,
                dm.release_year,
                fmr.avg_rating,
                fmr.total_ratings,
                STRING_AGG(DISTINCT dg.genre_name, ', ' ORDER BY dg.genre_name) as genres_str
            FROM gold.dim_movies dm
            JOIN gold.fact_movie_ratings fmr ON dm.movieid = fmr.movieid
            LEFT JOIN gold.fact_movie_genres fmg ON dm.movieid = fmg.movieid
            LEFT JOIN gold.dim_genres dg ON fmg.genre_id = dg.genre_id
            {base_filter}
            {genre_filter}
            GROUP BY dm.movieid, dm.title, dm.release_year, fmr.avg_rating, fmr.total_ratings
            ORDER BY fmr.avg_rating DESC, fmr.total_ratings DESC
            LIMIT :limit OFFSET :offset
        """
        
        # Get total count
        total = self.db.execute(text(count_sql), params).scalar() or 0
        
        # Get data
        results = self.db.execute(text(data_sql), params).fetchall()
        
        movies = [
            {
                "movieid": r.movieid,
                "title": r.title,
                "release_year": r.release_year,
                "avg_rating": round(r.avg_rating, 2),
                "total_ratings": r.total_ratings,
                "genres": r.genres_str.split(', ') if r.genres_str else []
            }
            for r in results
        ]
        
        return movies, total
    
    # ============ GRÁFICOS ============
    def get_movies_by_decade(self) -> List[Dict[str, Any]]:
        """Get movies count grouped by decade"""
        query = text("""
            SELECT 
                FLOOR(release_year / 10) * 10 as decade,
                COUNT(*) as count
            FROM gold.dim_movies
            WHERE release_year IS NOT NULL
            GROUP BY decade
            ORDER BY decade
        """)
        results = self.db.execute(query).fetchall()
        return [{"decade": r.decade, "count": r.count} for r in results]
    
    def get_rating_distribution(self) -> List[Dict[str, Any]]:
        """Get rating distribution"""
        query = text("""
            SELECT 
                CASE 
                    WHEN avg_rating < 1 THEN '0-1'
                    WHEN avg_rating < 2 THEN '1-2'
                    WHEN avg_rating < 3 THEN '2-3'
                    WHEN avg_rating < 4 THEN '3-4'
                    ELSE '4-5'
                END as rating_range,
                COUNT(*) as count
            FROM gold.fact_movie_ratings
            GROUP BY rating_range
            ORDER BY rating_range
        """)
        results = self.db.execute(query).fetchall()
        return [{"rating_range": r.rating_range, "count": r.count} for r in results]