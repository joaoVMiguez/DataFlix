"""
TMDB response models
"""
from pydantic import BaseModel
from typing import List, Optional

class TMDBStats(BaseModel):
    total_movies: int
    total_revenue: str  # "US$ 12,4 bi"
    total_budget: str   # "US$ 1,5 bi"
    total_profit: str   # "US$ 10,9 bi"

class MovieFinancial(BaseModel):
    movieid: int
    tmdb_id: str
    title: str
    release_year: Optional[int] = None
    revenue: int
    budget: int
    profit: int
    roi: float

class CountryPerformance(BaseModel):
    country_code: str
    country_name: str
    total_movies: int
    avg_budget: int
    avg_revenue: int
    avg_roi: float
    total_profit: int
    top_genre: str
    most_profitable_studio: Optional[str] = None

class StudioPerformance(BaseModel):
    company_id: int
    company_name: str
    total_movies: int
    total_budget: int
    total_revenue: int
    total_profit: int
    avg_roi: float
    success_rate: float
    top_movie_title: str
    top_movie_revenue: int

class TMDBResponse(BaseModel):
    stats: TMDBStats
    top_movies: List[MovieFinancial]
    avg_revenue: int
    avg_budget: int
    avg_roi: float