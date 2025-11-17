"""
Box Office business logic service
"""
from typing import List
from ..repositories.box_office_repository import BoxOfficeRepository
from ..models.box_office import (
    BoxOfficeResponse,
    BoxOfficeStats,
    BoxOfficeMovie,
    PerformanceIndicators,
    FinancialPerformance
)
import logging

logger = logging.getLogger(__name__)

class BoxOfficeService:
    def __init__(self, repository: BoxOfficeRepository):
        self.repository = repository
    
    def get_analytics(self) -> BoxOfficeResponse:
        """Get complete Box Office analytics"""
        try:
            # Get statistics
            stats_data = self.repository.get_stats()
            stats = BoxOfficeStats(**stats_data)
            
            # Get top profitable movies
            top_movies_data = self.repository.get_top_profitable_movies(limit=5)
            top_movies = [BoxOfficeMovie(**movie) for movie in top_movies_data]
            
            # Get performance indicators
            indicators_data = self.repository.get_performance_indicators()
            indicators = PerformanceIndicators(**indicators_data)
            
            # Get highest profit movie
            highest_profit = self.repository.get_highest_profit()
            financial_performance = FinancialPerformance(**highest_profit)
            
            return BoxOfficeResponse(
                stats=stats,
                top_movies=top_movies,
                performance_indicators=indicators,
                financial_performance=financial_performance
            )
        except Exception as e:
            logger.error(f"Error getting Box Office analytics: {e}")
            raise
    
    def get_top_movies(self, limit: int = 10) -> List[BoxOfficeMovie]:
        """Get top profitable movies"""
        try:
            data = self.repository.get_top_profitable_movies(limit)
            return [BoxOfficeMovie(**movie) for movie in data]
        except Exception as e:
            logger.error(f"Error getting top box office movies: {e}")
            raise