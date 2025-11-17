"""
TMDB business logic service
"""
from typing import List
from ..repositories.tmdb_repository import TMDBRepository
from ..models.tmdb import (
    TMDBResponse,
    TMDBStats,
    MovieFinancial,
    CountryPerformance,
    StudioPerformance
)
import logging

logger = logging.getLogger(__name__)

class TMDBService:
    def __init__(self, repository: TMDBRepository):
        self.repository = repository
    
    def get_analytics(self) -> TMDBResponse:
        """Get complete TMDB analytics"""
        try:
            # Get statistics
            stats_data = self.repository.get_stats()
            stats = TMDBStats(**stats_data)
            
            # Get top movies by revenue
            top_movies_data = self.repository.get_top_movies_by_revenue(limit=5)
            top_movies = [MovieFinancial(**movie) for movie in top_movies_data]
            
            # Get averages
            averages = self.repository.get_averages()
            
            return TMDBResponse(
                stats=stats,
                top_movies=top_movies,
                avg_revenue=averages["avg_revenue"],
                avg_budget=averages["avg_budget"],
                avg_roi=averages["avg_roi"]
            )
        except Exception as e:
            logger.error(f"Error getting TMDB analytics: {e}")
            raise
    
    def get_country_performance(self, limit: int = 10) -> List[CountryPerformance]:
        """Get performance metrics by country"""
        try:
            data = self.repository.get_country_performance(limit)
            return [CountryPerformance(**country) for country in data]
        except Exception as e:
            logger.error(f"Error getting country performance: {e}")
            raise
    
    def get_studio_performance(self, limit: int = 10) -> List[StudioPerformance]:
        """Get performance metrics by studio"""
        try:
            data = self.repository.get_studio_performance(limit)
            return [StudioPerformance(**studio) for studio in data]
        except Exception as e:
            logger.error(f"Error getting studio performance: {e}")
            raise
    
    def search_movies(self, query: str, limit: int = 20) -> List[MovieFinancial]:
        """Search movies in TMDB data"""
        try:
            results = self.repository.search_movies(query, limit)
            return [MovieFinancial(**movie) for movie in results]
        except Exception as e:
            logger.error(f"Error searching TMDB movies: {e}")
            raise