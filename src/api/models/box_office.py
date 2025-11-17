"""
Box Office response models
"""
from pydantic import BaseModel
from typing import List, Optional

class BoxOfficeStats(BaseModel):
    total_revenue: str  # "US$ 7,7 bi"
    total_profit: str   # "US$ 7,2 bi"
    avg_roi: str        # "1434%"
    blockbusters_count: int

class BoxOfficeMovie(BaseModel):
    movielens_id: int
    title: str
    release_year: Optional[int] = None
    budget: int
    revenue: int
    profit: int
    roi: float
    payback_ratio: float
    budget_category: str
    revenue_category: Optional[str] = None
    roi_category: Optional[str] = None
    is_blockbuster: bool
    is_profitable: bool

class PerformanceIndicators(BaseModel):
    profitability_rate: float
    avg_blockbusters: float

class FinancialPerformance(BaseModel):
    highest_profit_movie: str
    highest_profit_value: int

class BoxOfficeResponse(BaseModel):
    stats: BoxOfficeStats
    top_movies: List[BoxOfficeMovie]
    performance_indicators: PerformanceIndicators
    financial_performance: FinancialPerformance