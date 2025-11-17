"""
TMDB data repository
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TMDBRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_stats(self) -> Dict[str, Any]:
        """Get TMDB statistics"""
        query = text("""
            SELECT 
                COUNT(DISTINCT movielens_id) as total_movies,
                SUM(revenue) as total_revenue,
                SUM(budget) as total_budget,
                SUM(profit) as total_profit
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
        """)
        result = self.db.execute(query).fetchone()
        
        total_revenue = result.total_revenue or 0
        total_budget = result.total_budget or 0
        total_profit = result.total_profit or 0
        
        return {
            "total_movies": result.total_movies or 0,
            "total_revenue": f"US$ {total_revenue / 1_000_000_000:.1f} bi",
            "total_budget": f"US$ {total_budget / 1_000_000_000:.1f} bi",
            "total_profit": f"US$ {total_profit / 1_000_000_000:.1f} bi"
        }
    
    def get_top_movies_by_revenue(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top movies by revenue"""
        query = text("""
            SELECT 
                movielens_id as movieid,
                tmdb_id,
                title,
                release_year,
                revenue,
                budget,
                profit,
                roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
            ORDER BY revenue DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "tmdb_id": str(r.tmdb_id),
                "title": r.title,
                "release_year": r.release_year,
                "revenue": r.revenue,
                "budget": r.budget,
                "profit": r.profit,
                "roi": round(r.roi, 2) if r.roi else 0
            }
            for r in results
        ]
    
    def get_averages(self) -> Dict[str, Any]:
        """Get average financial metrics"""
        query = text("""
            SELECT 
                AVG(revenue) as avg_revenue,
                AVG(budget) as avg_budget,
                AVG(roi) as avg_roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE has_revenue = true AND has_budget = true
        """)
        result = self.db.execute(query).fetchone()
        
        return {
            "avg_revenue": int(result.avg_revenue or 0),
            "avg_budget": int(result.avg_budget or 0),
            "avg_roi": round(result.avg_roi or 0, 2)
        }
    
    def get_country_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get performance by country"""
        query = text("""
            SELECT 
                country_code,
                country_name,
                total_movies,
                avg_budget,
                avg_revenue,
                avg_roi,
                total_profit,
                top_genre
            FROM gold_tmdb.fact_country_performance
            ORDER BY total_profit DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "country_code": r.country_code,
                "country_name": r.country_name,
                "total_movies": r.total_movies,
                "avg_budget": r.avg_budget,
                "avg_revenue": r.avg_revenue,
                "avg_roi": r.avg_roi,
                "total_profit": r.total_profit,
                "top_genre": r.top_genre,
                "most_profitable_studio": None  # Campo não existe na tabela
            }
            for r in results
        ]
    
    def get_studio_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get performance by studio"""
        query = text("""
            SELECT 
                company_id,
                company_name,
                total_movies,
                total_budget,
                total_revenue,
                total_profit,
                avg_roi,
                success_rate,
                top_movie_title,
                top_movie_revenue
            FROM gold_tmdb.fact_studio_performance
            ORDER BY total_profit DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [dict(r._mapping) for r in results]
    
    def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search movies in TMDB data"""
        sql = text("""
            SELECT 
                movielens_id as movieid,
                tmdb_id,
                title,
                release_year,
                revenue,
                budget,
                profit,
                roi
            FROM gold_tmdb.dim_movies_tmdb
            WHERE LOWER(title) LIKE LOWER(:query)
            AND has_revenue = true 
            AND has_budget = true
            ORDER BY revenue DESC
            LIMIT :limit
        """)
        
        results = self.db.execute(sql, {"query": f"%{query}%", "limit": limit}).fetchall()
        
        return [
            {
                "movieid": r.movieid,
                "tmdb_id": str(r.tmdb_id),
                "title": r.title,
                "release_year": r.release_year,
                "revenue": r.revenue,
                "budget": r.budget,
                "profit": r.profit,
                "roi": round(r.roi, 2) if r.roi else 0
            }
            for r in results
        ]