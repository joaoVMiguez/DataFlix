"""
TMDB response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional

# ============ ESTATÍSTICAS GERAIS ============
class TMDBStats(BaseModel):
    total_movies: int
    total_revenue: str # "US$ 12,4 bi"
    total_budget: str # "US$ 1,5 bi"
    total_profit: str # "US$ 10,9 bi"

# ============ FILMES ============
class MovieFinancial(BaseModel):
    movieid: int
    tmdb_id: Optional[str] = None # Pode ser None
    title: str
    release_year: Optional[int] = None
    revenue: int
    budget: int
    profit: int
    roi: float

class MovieDetail(BaseModel):
    movieid: int
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    title: str
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    runtime: Optional[int] = None
    budget: int
    revenue: int
    profit: int
    roi: float
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    genres: List[str] = []
    main_production_company: Optional[str] = None
    main_country: Optional[str] = None
    overview: Optional[str] = None  # ← ADICIONAR
    poster_path: Optional[str] = None  # ← ADICIONAR
    
    class Config:
        from_attributes = True

# ============ PAÍSES ============
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

#============ STUDIOS ============
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

#============ BUSCA ============
class MovieSearchResult(BaseModel):
    movieid: int
    title: str
    release_year: Optional[int] = None
    revenue: Optional[int] = None
    budget: Optional[int] = None
    vote_average: Optional[float] = None
    genres: List[str] = []

# ============ PAGINAÇÃO ============
class TMDBMovieList(BaseModel):
    movies: List[MovieFinancial]
    total: int
    page: int
    page_size: int
    total_pages: int

# ============ RESPONSE PRINCIPAL ============
class TMDBResponse(BaseModel):
    stats: TMDBStats
    top_movies: List[MovieFinancial]
    avg_revenue: int
    avg_budget: int
    avg_roi: float
# ============ ANÁLISES ============
class RevenueByDecade(BaseModel):
    decade: int
    movie_count: int
    total_revenue: int
    avg_revenue: int

class GenreRevenue(BaseModel):
    genre: str
    total_movies: int
    total_revenue: int
    avg_revenue: int
    avg_roi: float