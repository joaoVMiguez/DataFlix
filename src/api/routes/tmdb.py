"""
TMDB API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..services.tmdb_service import TMDBService
from ..models.tmdb import (
    TMDBResponse,
    TMDBMovieList,
    MovieDetail,
    MovieSearchResult,
    StudioPerformance,
    CountryPerformance,
    RevenueByDecade,
    GenreRevenue,
    MovieFinancial
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tmdb", tags=["TMDB"])

# ============ DASHBOARD ============
@router.get("/", response_model=TMDBResponse)
async def get_tmdb_dashboard(db: Session = Depends(get_db)):
    """
    Get TMDB dashboard with statistics and top movies
    """
    try:
        service = TMDBService(db)
        return service.get_dashboard_data()
    except Exception as e:
        logger.error(f"Error in TMDB dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ FILMES ============
@router.get("/movies/top", response_model=List[MovieFinancial])
async def get_top_movies(
    limit: int = Query(10, ge=1, le=100, description="Number of movies to return"),
    order_by: str = Query("revenue", regex="^(revenue|profit|roi)$", description="Order criteria"),
    db: Session = Depends(get_db)
):
    """
    Get top movies by different criteria
    - **limit**: Number of movies (1-100)
    - **order_by**: revenue, profit, or roi
    """
    try:
        service = TMDBService(db)
        return service.get_top_movies(limit=limit, order_by=order_by)
    except Exception as e:
        logger.error(f"Error getting top movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ⚠️ IMPORTANTE: Search ANTES de {movie_id} ⚠️
@router.get("/movies/search", response_model=List[MovieSearchResult])
async def search_movies(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search movies by title
    - **q**: Search query (minimum 2 characters)
    - **limit**: Maximum results (1-100)
    """
    try:
        service = TMDBService(db)
        return service.search_movies(query=q, limit=limit)
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movies", response_model=TMDBMovieList)
async def get_movies_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    order_by: str = Query("popularity", regex="^(popularity|revenue|rating)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of movies
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page (1-100)
    - **order_by**: popularity, revenue, or rating
    """
    try:
        service = TMDBService(db)
        return service.get_movies_paginated(
            page=page,
            page_size=page_size,
            order_by=order_by
        )
    except Exception as e:
        logger.error(f"Error getting paginated movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movies/{movie_id}", response_model=MovieDetail)
async def get_movie_detail(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific movie
    - **movie_id**: MovieLens ID
    """
    try:
        service = TMDBService(db)
        movie = service.get_movie_by_id(movie_id)
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        return movie
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting movie {movie_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ STUDIOS ============
@router.get("/studios", response_model=List[StudioPerformance])
async def get_studio_performance(
    limit: int = Query(20, ge=1, le=100, description="Number of studios"),
    db: Session = Depends(get_db)
):
    """
    Get studio performance statistics
    - **limit**: Number of studios to return (1-100)
    """
    try:
        service = TMDBService(db)
        return service.get_studio_performance(limit=limit)
    except Exception as e:
        logger.error(f"Error getting studio performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ PAÍSES ============
@router.get("/countries", response_model=List[CountryPerformance])
async def get_country_performance(
    limit: int = Query(20, ge=1, le=100, description="Number of countries"),
    db: Session = Depends(get_db)
):
    """
    Get country performance statistics
    - **limit**: Number of countries to return (1-100)
    """
    try:
        service = TMDBService(db)
        return service.get_country_performance(limit=limit)
    except Exception as e:
        logger.error(f"Error getting country performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ ANÁLISES ============
@router.get("/analytics/revenue-by-decade", response_model=List[RevenueByDecade])
async def get_revenue_by_decade(db: Session = Depends(get_db)):
    """
    Get revenue analysis grouped by decade
    """
    try:
        service = TMDBService(db)
        return service.get_revenue_by_decade()
    except Exception as e:
        logger.error(f"Error getting revenue by decade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/genre-revenue", response_model=List[GenreRevenue])
async def get_genre_revenue(db: Session = Depends(get_db)):
    """
    Get revenue analysis grouped by genre
    """
    try:
        service = TMDBService(db)
        return service.get_genre_revenue()
    except Exception as e:
        logger.error(f"Error getting genre revenue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))