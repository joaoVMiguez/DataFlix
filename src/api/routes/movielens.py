"""
MovieLens API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..repositories.movielens_repository import MovieLensRepository
from ..services.movielens_service import MovieLensService
from ..models.movielens import MovieLensResponse, MovieSearchResult, GenreStats
from ..models.common import SuccessResponse, PaginatedResponse
from ..dependencies import get_movielens_repository

router = APIRouter(prefix="/movielens", tags=["MovieLens"])

@router.get("/analytics", response_model=SuccessResponse[MovieLensResponse])
async def get_movielens_analytics(
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """
    Get complete MovieLens analytics including:
    - General statistics
    - Top rated movies
    - Genre statistics
    """
    service = MovieLensService(repo)
    data = service.get_analytics()
    return SuccessResponse(data=data, message="MovieLens analytics retrieved successfully")

# ============ NOVA ROTA DE PAGINAÇÃO ============
@router.get("/movies", response_model=SuccessResponse[PaginatedResponse])
async def get_movies_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """
    Get paginated list of top movies
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **genre**: Optional genre filter
    """
    service = MovieLensService(repo)
    data = service.get_movies_paginated(page=page, page_size=page_size, genre=genre)
    return SuccessResponse(data=data, message=f"Retrieved page {page} of movies")

@router.get("/search", response_model=SuccessResponse[list[MovieSearchResult]])
async def search_movies(
    q: str = Query(..., min_length=1, description="Search query"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """
    Search movies by title with optional genre filter
    """
    service = MovieLensService(repo)
    results = service.search_movies(q, genre, limit)
    return SuccessResponse(data=results, message=f"Found {len(results)} movies")

@router.get("/movies/{movie_id}")
async def get_movie_details(
    movie_id: int,
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """
    Get detailed information about a specific movie
    """
    service = MovieLensService(repo)
    movie = service.get_movie_details(movie_id)
    
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    
    return SuccessResponse(data=movie, message="Movie details retrieved successfully")

@router.get("/genres", response_model=SuccessResponse[list[GenreStats]])
async def get_genres(
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """
    Get all genres with statistics
    """
    service = MovieLensService(repo)
    genres = service.get_genres()
    return SuccessResponse(data=genres, message="Genres retrieved successfully")

# ============ ROTAS PARA GRÁFICOS ============
@router.get("/charts/genre-distribution")
async def get_genre_distribution(
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """Get data for genre distribution chart"""
    service = MovieLensService(repo)
    data = service.get_genre_distribution()
    return SuccessResponse(data=data, message="Chart data retrieved")

@router.get("/charts/movies-by-decade")
async def get_movies_by_decade(
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """Get movies count grouped by decade"""
    service = MovieLensService(repo)
    data = service.get_movies_by_decade()
    return SuccessResponse(data=data, message="Chart data retrieved")

@router.get("/charts/rating-distribution")
async def get_rating_distribution(
    repo: MovieLensRepository = Depends(get_movielens_repository)
):
    """Get distribution of ratings"""
    service = MovieLensService(repo)
    data = service.get_rating_distribution()
    return SuccessResponse(data=data, message="Chart data retrieved")