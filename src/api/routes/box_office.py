"""
Box Office API endpoints
"""
from fastapi import APIRouter, Depends, Query
from ..repositories.box_office_repository import BoxOfficeRepository
from ..services.box_office_service import BoxOfficeService
from ..models.box_office import BoxOfficeResponse, BoxOfficeMovie
from ..models.common import SuccessResponse
from ..dependencies import get_box_office_repository

router = APIRouter(prefix="/box-office", tags=["Box Office"])

@router.get("/analytics", response_model=SuccessResponse[BoxOfficeResponse])
async def get_box_office_analytics(
    repo: BoxOfficeRepository = Depends(get_box_office_repository)
):
    """
    Get complete Box Office analytics including:
    - Total revenue, profit and ROI
    - Most profitable movies
    - Performance indicators
    - Blockbuster statistics
    """
    service = BoxOfficeService(repo)
    data = service.get_analytics()
    return SuccessResponse(data=data, message="Box Office analytics retrieved successfully")

@router.get("/top-movies", response_model=SuccessResponse[list[BoxOfficeMovie]])
async def get_top_box_office_movies(
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    repo: BoxOfficeRepository = Depends(get_box_office_repository)
):
    """
    Get top profitable movies from box office
    """
    service = BoxOfficeService(repo)
    data = service.get_top_movies(limit)
    return SuccessResponse(data=data, message=f"Top {len(data)} profitable movies retrieved")