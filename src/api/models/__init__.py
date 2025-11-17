"""
Pydantic models for API responses
"""
from .common import SuccessResponse, ErrorResponse
from .movielens import MovieLensStats, MovieDetail, GenreStats, MovieSearchResult, MovieLensResponse
from .tmdb import TMDBStats, MovieFinancial, CountryPerformance, StudioPerformance, TMDBResponse
from .box_office import BoxOfficeStats, BoxOfficeMovie, PerformanceIndicators, FinancialPerformance, BoxOfficeResponse

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "MovieLensStats",
    "MovieDetail",
    "GenreStats",
    "MovieSearchResult",
    "MovieLensResponse",
    "TMDBStats",
    "MovieFinancial",
    "CountryPerformance",
    "StudioPerformance",
    "TMDBResponse",
    "BoxOfficeStats",
    "BoxOfficeMovie",
    "PerformanceIndicators",
    "FinancialPerformance",
    "BoxOfficeResponse",
]