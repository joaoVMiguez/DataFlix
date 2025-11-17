"""
MovieLens response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class MovieLensStats(BaseModel):
    total_movies: int
    total_ratings: str  # "20M+"
    avg_rating: float
    active_users: int

class MovieDetail(BaseModel):
    movieid: int
    title: str
    release_year: Optional[int] = None  # Pode ser None
    avg_rating: float
    total_ratings: int
    genres: List[str] = Field(default_factory=list)
    description: Optional[str] = None 
    poster_path: Optional[str] = None

class GenreStats(BaseModel):
    genre_id: int
    genre_name: str
    total_movies: int
    total_ratings: int
    avg_rating: float

class MovieSearchResult(BaseModel):
    movieid: int
    title: str
    release_year: Optional[int] = None
    genres: str = ""
    avg_rating: float
    total_ratings: int

class MovieLensResponse(BaseModel):
    stats: MovieLensStats
    top_movies: List[MovieDetail]
    genres: List[GenreStats]