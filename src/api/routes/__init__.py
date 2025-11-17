"""
API Routes
"""
from .movielens import router as movielens_router
from .tmdb import router as tmdb_router
from .box_office import router as box_office_router
from .health import router as health_router

__all__ = [
    "movielens_router",
    "tmdb_router",
    "box_office_router",
    "health_router",
]