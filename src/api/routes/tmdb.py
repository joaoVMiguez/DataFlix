"""
TMDB API endpoints
"""
from fastapi import APIRouter, Depends, Query
from ..repositories.tmdb_repository import TMDBRepository
from ..services.tmdb_service import TMDBService
from ..models.tmdb import TMDBResponse, CountryPerformance, StudioPerformance, MovieFinancial
from ..models.common import SuccessResponse
from ..dependencies import get_tmdb_repository

router = APIRouter(prefix="/tmdb", tags=["TMDB"])

@router.get("/analytics", response_model=SuccessResponse[TMDBResponse])
async def get_tmdb_analytics(
    repo: TMDBRepository = Depends(get_tmdb_repository)
):
    """
    Get complete TMDB analytics including:
    - Revenue, budget and profit statistics
    - Top movies by revenue
    - Average financial metrics
    """
    service = TMDBService(repo)
    data = service.get_analytics()
    return SuccessResponse(data=data, message="TMDB analytics retrieved successfully")

@router.get("/countries", response_model=SuccessResponse[list[CountryPerformance]])
async def get_country_performance(
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    repo: TMDBRepository = Depends(get_tmdb_repository)
):
    """
    Get performance metrics by country
    """
    service = TMDBService(repo)
    data = service.get_country_performance(limit)
    return SuccessResponse(data=data, message="Country performance retrieved successfully")

@router.get("/studios", response_model=SuccessResponse[list[StudioPerformance]])
async def get_studio_performance(
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    repo: TMDBRepository = Depends(get_tmdb_repository)
):
    """
    Get performance metrics by studio/production company
    """
    service = TMDBService(repo)
    data = service.get_studio_performance(limit)
    return SuccessResponse(data=data, message="Studio performance retrieved successfully")

@router.get("/search", response_model=SuccessResponse[list[MovieFinancial]])
async def search_tmdb_movies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    repo: TMDBRepository = Depends(get_tmdb_repository)
):
    """
    Search movies in TMDB data
    """
    service = TMDBService(repo)
    results = service.search_movies(q, limit)
    return SuccessResponse(data=results, message=f"Found {len(results)} movies")