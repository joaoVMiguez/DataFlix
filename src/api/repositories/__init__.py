"""
Data access layer - Repositories
"""
from .movielens_repository import MovieLensRepository
from .tmdb_repository import TMDBRepository
from .box_office_repository import BoxOfficeRepository

__all__ = [
    "MovieLensRepository",
    "TMDBRepository",
    "BoxOfficeRepository",
]