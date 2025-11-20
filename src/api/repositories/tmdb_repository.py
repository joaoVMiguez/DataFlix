"""
TMDB data repository
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TMDBRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # ============ ESTATÍSTICAS GERAIS ============
    def get_stats(self) -> Dict[str, Any]:
        """Get general TMDB statistics"""
        query = text("""
            SELECT 
                COUNT(DISTINCT movielens_id) as total_movies,
                COALESCE(SUM(revenue), 0) as total_revenue,
                COALESCE(SUM(budget), 0) as total_budget,
                COALESCE(SUM(profit), 0) as total_profit
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
        """)
        result = self.db.execute(query).fetchone()
        
        return {
            "total_movies": result.total_movies or 0,
            "total_revenue": int(result.total_revenue or 0),
            "total_budget": int(result.total_budget or 0),
            "total_profit": int(result.total_profit or 0)
        }
    
    def get_avg_stats(self) -> Dict[str, Any]:
        """Get average statistics"""
        query = text("""
            SELECT 
                COALESCE(AVG(revenue), 0) as avg_revenue,
                COALESCE(AVG(budget), 0) as avg_budget,
                COALESCE(AVG(roi), 0) as avg_roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
        """)
        result = self.db.execute(query).fetchone()
        
        return {
            "avg_revenue": int(result.avg_revenue or 0),
            "avg_budget": int(result.avg_budget or 0),
            "avg_roi": round(float(result.avg_roi or 0), 2)
        }
    
    # ============ TOP FILMES ============
    def get_top_movies(self, limit: int = 10, order_by: str = "revenue") -> List[Dict[str, Any]]:
        """
        Get top movies by different criteria
        order_by: 'revenue', 'profit', 'roi'
        """
        order_clause = {
            "revenue": "revenue DESC NULLS LAST",
            "profit": "profit DESC NULLS LAST",
            "roi": "roi DESC NULLS LAST"
        }.get(order_by, "revenue DESC NULLS LAST")
        
        query = text(f"""
            SELECT 
                movielens_id as movieid,
                CAST(tmdb_id AS TEXT) as tmdb_id,
                title,
                release_year,
                COALESCE(budget, 0) as budget,
                COALESCE(revenue, 0) as revenue,
                COALESCE(profit, 0) as profit,
                COALESCE(roi, 0.0) as roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
            ORDER BY {order_clause}
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "tmdb_id": r.tmdb_id,
                "title": r.title,
                "release_year": r.release_year,
                "budget": int(r.budget),
                "revenue": int(r.revenue),
                "profit": int(r.profit),
                "roi": round(float(r.roi), 2)
            }
            for r in results
        ]
    
    # ============ STUDIOS ============
    def get_studio_performance(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing studios"""
        query = text("""
            SELECT 
                company_id,
                company_name,
                total_movies,
                COALESCE(total_budget, 0) as total_budget,
                COALESCE(total_revenue, 0) as total_revenue,
                COALESCE(total_profit, 0) as total_profit,
                COALESCE(avg_roi, 0.0) as avg_roi,
                COALESCE(success_rate, 0.0) as success_rate,
                top_movie_title,
                COALESCE(top_movie_revenue, 0) as top_movie_revenue
            FROM gold_tmdb.fact_studio_performance
            ORDER BY total_revenue DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "company_id": r.company_id,
                "company_name": r.company_name,
                "total_movies": r.total_movies,
                "total_budget": int(r.total_budget),
                "total_revenue": int(r.total_revenue),
                "total_profit": int(r.total_profit),
                "avg_roi": round(float(r.avg_roi), 2),
                "success_rate": round(float(r.success_rate), 2),
                "top_movie_title": r.top_movie_title,
                "top_movie_revenue": int(r.top_movie_revenue)
            }
            for r in results
        ]
    
    # ============ PAÍSES ============
    def get_country_performance(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get country performance statistics"""
        query = text("""
            SELECT 
                country_code,
                country_name,
                total_movies,
                COALESCE(avg_budget, 0) as avg_budget,
                COALESCE(avg_revenue, 0) as avg_revenue,
                COALESCE(avg_roi, 0.0) as avg_roi,
                COALESCE(total_profit, 0) as total_profit,
                top_genre,
                most_prolific_studio
            FROM gold_tmdb.fact_country_performance
            ORDER BY total_movies DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "country_code": r.country_code,
                "country_name": r.country_name,
                "total_movies": r.total_movies,
                "avg_budget": int(r.avg_budget),
                "avg_revenue": int(r.avg_revenue),
                "avg_roi": round(float(r.avg_roi), 2),
                "total_profit": int(r.total_profit),
                "top_genre": r.top_genre,
                "most_profitable_studio": r.most_prolific_studio
            }
            for r in results
        ]
    
    # ============ BUSCA E DETALHES ============
    def search_movies(
        self, 
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search movies by title"""
        sql = text("""
            SELECT 
                movielens_id as movieid,
                title,
                release_year,
                COALESCE(revenue, 0) as revenue,
                COALESCE(budget, 0) as budget,
                vote_average,
                genres_list
            FROM gold_tmdb.dim_movies_tmdb
            WHERE LOWER(title) LIKE LOWER(:query)
               OR LOWER(original_title) LIKE LOWER(:query)
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit
        """)
        
        results = self.db.execute(sql, {"query": f"%{query}%", "limit": limit}).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "title": r.title,
                "release_year": r.release_year,
                "revenue": int(r.revenue) if r.revenue else None,
                "budget": int(r.budget) if r.budget else None,
                "vote_average": round(float(r.vote_average), 2) if r.vote_average else None,
                "genres": r.genres_list.split(', ') if r.genres_list else []
            }
            for r in results
        ]
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by MovieLens ID"""
        query = text("""
            SELECT 
                dm.movielens_id as movieid,
                CAST(dm.tmdb_id AS TEXT) as tmdb_id,
                CAST(dm.imdb_id AS TEXT) as imdb_id,
                dm.title,
                dm.original_title,
                dm.release_year,
                dm.runtime,
                COALESCE(dm.budget, 0) as budget,
                COALESCE(dm.revenue, 0) as revenue,
                COALESCE(dm.profit, 0) as profit,
                COALESCE(dm.roi, 0.0) as roi,
                dm.vote_average,
                dm.vote_count,
                dm.popularity,
                dm.genres_list,
                dm.main_production_company,
                dm.main_country,
                sm.overview,
                sm.poster_path
            FROM gold_tmdb.dim_movies_tmdb dm
            LEFT JOIN silver_tmdb.movies_tmdb sm ON dm.movielens_id = sm.movielens_id
            WHERE dm.movielens_id = :movie_id
        """)
        
        result = self.db.execute(query, {"movie_id": movie_id}).fetchone()
        
        if not result:
            return None
        
        return {
            "movieid": result.movieid,
            "tmdb_id": result.tmdb_id,
            "imdb_id": result.imdb_id,
            "title": result.title,
            "original_title": result.original_title,
            "release_year": result.release_year,
            "runtime": result.runtime,
            "budget": int(result.budget),
            "revenue": int(result.revenue),
            "profit": int(result.profit),
            "roi": round(float(result.roi), 2),
            "vote_average": round(float(result.vote_average), 2) if result.vote_average else None,
            "vote_count": result.vote_count,
            "popularity": round(float(result.popularity), 2) if result.popularity else None,
            "genres": result.genres_list.split(', ') if result.genres_list else [],
            "main_production_company": result.main_production_company,
            "main_country": result.main_country,
            "overview": result.overview,  # ← ADICIONAR
            "poster_path": result.poster_path  # ← ADICIONAR
        }
    
    # ============ PAGINAÇÃO ============
    def get_movies_paginated(
        self, 
        limit: int = 20, 
        offset: int = 0,
        order_by: str = "popularity"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated movies"""
        
        order_clause = {
            "popularity": "popularity DESC NULLS LAST",
            "revenue": "revenue DESC NULLS LAST",
            "rating": "vote_average DESC NULLS LAST"
        }.get(order_by, "popularity DESC NULLS LAST")
        
        # Count query
        count_sql = """
            SELECT COUNT(*) as total
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
        """
        
        # Data query
        data_sql = f"""
            SELECT 
                movielens_id as movieid,
                CAST(tmdb_id AS TEXT) as tmdb_id,
                title,
                release_year,
                COALESCE(budget, 0) as budget,
                COALESCE(revenue, 0) as revenue,
                COALESCE(profit, 0) as profit,
                COALESCE(roi, 0.0) as roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
            ORDER BY {order_clause}
            LIMIT :limit OFFSET :offset
        """
        
        params = {"limit": limit, "offset": offset}
        
        # Get total count
        total = self.db.execute(text(count_sql)).scalar() or 0
        
        # Get data
        results = self.db.execute(text(data_sql), params).fetchall()
        
        movies = [
            {
                "movieid": r.movieid,
                "tmdb_id": r.tmdb_id,
                "title": r.title,
                "release_year": r.release_year,
                "budget": int(r.budget),
                "revenue": int(r.revenue),
                "profit": int(r.profit),
                "roi": round(float(r.roi), 2)
            }
            for r in results
        ]
        
        return movies, total
    
    # ============ ANÁLISES ============
    def get_revenue_by_decade(self) -> List[Dict[str, Any]]:
        """Get total revenue grouped by decade"""
        query = text("""
            SELECT 
                release_decade as decade,
                COUNT(*) as movie_count,
                COALESCE(SUM(revenue), 0) as total_revenue,
                COALESCE(AVG(revenue), 0) as avg_revenue
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND release_decade IS NOT NULL
            GROUP BY release_decade
            ORDER BY release_decade
        """)
        results = self.db.execute(query).fetchall()
        
        return [
            {
                "decade": r.decade,
                "movie_count": r.movie_count,
                "total_revenue": int(r.total_revenue),
                "avg_revenue": int(r.avg_revenue)
            }
            for r in results
        ]
    
    def get_genre_revenue(self) -> List[Dict[str, Any]]:
        """Get revenue by genre"""
        query = text("""
            WITH genre_split AS (
                SELECT 
                    movielens_id,
                    TRIM(UNNEST(STRING_TO_ARRAY(genres_list, ','))) as genre,
                    revenue,
                    roi
                FROM gold_tmdb.dim_movies_tmdb
                WHERE has_revenue = true AND genres_list IS NOT NULL
            )
            SELECT 
                genre,
                COUNT(*) as total_movies,
                COALESCE(SUM(revenue), 0) as total_revenue,
                COALESCE(AVG(revenue), 0) as avg_revenue,
                COALESCE(AVG(roi), 0.0) as avg_roi
            FROM genre_split
            GROUP BY genre
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        results = self.db.execute(query).fetchall()
        
        return [
            {
                "genre": r.genre,
                "total_movies": r.total_movies,
                "total_revenue": int(r.total_revenue),
                "avg_revenue": int(r.avg_revenue),
                "avg_roi": round(float(r.avg_roi), 2)
            }
            for r in results
        ]