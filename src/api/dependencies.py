"""
Shared dependencies for API routes
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .repositories.movielens_repository import MovieLensRepository
from .repositories.tmdb_repository import TMDBRepository
from .repositories.box_office_repository import BoxOfficeRepository

# Dependency factories
def get_movielens_repository(db: Session = Depends(get_db)) -> MovieLensRepository:
    return MovieLensRepository(db)

def get_tmdb_repository(db: Session = Depends(get_db)) -> TMDBRepository:
    return TMDBRepository(db)

def get_box_office_repository(db: Session = Depends(get_db)) -> BoxOfficeRepository:
    return BoxOfficeRepository(db)