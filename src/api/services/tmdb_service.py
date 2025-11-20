"""
TMDB business logic service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from ..repositories.tmdb_repository import TMDBRepository
from ..models.tmdb import (
    TMDBStats,
    MovieFinancial,
    StudioPerformance,
    CountryPerformance,
    MovieSearchResult,
    MovieDetail,
    TMDBMovieList,
    TMDBResponse,
    RevenueByDecade,
    GenreRevenue
)

logger = logging.getLogger(__name__)

class TMDBService:
    def __init__(self, db: Session):
        self.repository = TMDBRepository(db)
    
    def _format_currency(self, value: int) -> str:
        """Format currency value to billions/millions"""
        if value >= 1_000_000_000:
            return f"US$ {value / 1_000_000_000:.1f} bi"
        elif value >= 1_000_000:
            return f"US$ {value / 1_000_000:.1f} mi"
        else:
            return f"US$ {value:,.0f}"
    
    # ============ DASHBOARD PRINCIPAL ============
    def get_dashboard_data(self) -> TMDBResponse:
        """Get complete dashboard data"""
        try:
            # Get statistics
            stats_raw = self.repository.get_stats()
            avg_stats = self.repository.get_avg_stats()
            
            # Format stats
            stats = TMDBStats(
                total_movies=stats_raw["total_movies"],
                total_revenue=self._format_currency(stats_raw["total_revenue"]),
                total_budget=self._format_currency(stats_raw["total_budget"]),
                total_profit=self._format_currency(stats_raw["total_profit"])
            )
            
            # Get top movies
            top_movies_raw = self.repository.get_top_movies(limit=10)
            top_movies = [MovieFinancial(**movie) for movie in top_movies_raw]
            
            return TMDBResponse(
                stats=stats,
                top_movies=top_movies,
                avg_revenue=avg_stats["avg_revenue"],
                avg_budget=avg_stats["avg_budget"],
                avg_roi=avg_stats["avg_roi"]
            )
        
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    # ============ FILMES ============
    def get_top_movies(
        self, 
        limit: int = 10, 
        order_by: str = "revenue"
    ) -> List[MovieFinancial]:
        """Get top movies by criteria"""
        try:
            movies = self.repository.get_top_movies(limit=limit, order_by=order_by)
            return [MovieFinancial(**movie) for movie in movies]
        except Exception as e:
            logger.error(f"Error getting top movies: {str(e)}")
            raise
    
    def get_movie_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        """Get movie details by ID"""
        try:
            movie = self.repository.get_movie_by_id(movie_id)
            if movie:
                return MovieDetail(**movie)
            return None
        except Exception as e:
            logger.error(f"Error getting movie {movie_id}: {str(e)}")
            raise
    
    def search_movies(self, query: str, limit: int = 20) -> List[MovieSearchResult]:
        """Search movies by title"""
        try:
            results = self.repository.search_movies(query=query, limit=limit)
            return [MovieSearchResult(**result) for result in results]
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            raise
    
    # ============ PAGINAÇÃO ============
    def get_movies_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "popularity"
    ) -> TMDBMovieList:
        """Get paginated movie list"""
        try:
            offset = (page - 1) * page_size
            movies_raw, total = self.repository.get_movies_paginated(
                limit=page_size,
                offset=offset,
                order_by=order_by
            )
            
            movies = [MovieFinancial(**movie) for movie in movies_raw]
            total_pages = (total + page_size - 1) // page_size
            
            return TMDBMovieList(
                movies=movies,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f"Error getting paginated movies: {str(e)}")
            raise
    
    # ============ STUDIOS ============
    def get_studio_performance(self, limit: int = 20) -> List[StudioPerformance]:
        """Get studio performance data"""
        try:
            studios = self.repository.get_studio_performance(limit=limit)
            return [StudioPerformance(**studio) for studio in studios]
        except Exception as e:
            logger.error(f"Error getting studio performance: {str(e)}")
            raise
    
    # ============ PAÍSES ============
    def get_country_performance(self, limit: int = 20) -> List[CountryPerformance]:
        """Get country performance data"""
        try:
            countries = self.repository.get_country_performance(limit=limit)
            return [CountryPerformance(**country) for country in countries]
        except Exception as e:
            logger.error(f"Error getting country performance: {str(e)}")
            raise
    
    # ============ ANÁLISES ============
    def get_revenue_by_decade(self) -> List[RevenueByDecade]:
        """Get revenue analysis by decade"""
        try:
            data = self.repository.get_revenue_by_decade()
            return [RevenueByDecade(**item) for item in data]
        except Exception as e:
            logger.error(f"Error getting revenue by decade: {str(e)}")
            raise
    
    def get_genre_revenue(self) -> List[GenreRevenue]:
        """Get revenue analysis by genre"""
        try:
            data = self.repository.get_genre_revenue()
            return [GenreRevenue(**item) for item in data]
        except Exception as e:
            logger.error(f"Error getting genre revenue: {str(e)}")
            raise