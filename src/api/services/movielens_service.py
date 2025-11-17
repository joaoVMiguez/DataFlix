"""
MovieLens service layer
"""
from typing import Dict, Any, List, Optional
from ..repositories.movielens_repository import MovieLensRepository
import math

class MovieLensService:
    def __init__(self, repository: MovieLensRepository):
        self.repository = repository
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get complete MovieLens analytics"""
        stats = self.repository.get_stats()
        top_movies = self.repository.get_top_movies(limit=10)
        genres = self.repository.get_genre_stats()
        
        return {
            "stats": stats,
            "top_movies": top_movies,
            "genres": genres
        }
    
    # ============ NOVO MÉTODO DE PAGINAÇÃO ============
    def get_movies_paginated(
        self, 
        page: int = 1, 
        page_size: int = 10,
        genre: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated movies"""
        offset = (page - 1) * page_size
        movies, total = self.repository.get_movies_paginated(
            limit=page_size, 
            offset=offset,
            genre=genre
        )
        
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        return {
            "items": movies,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    
    def search_movies(
        self, 
        query: str, 
        genre: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search movies"""
        return self.repository.search_movies(query=query, genre=genre, limit=limit)
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get movie details by ID"""
        return self.repository.get_movie_by_id(movie_id)
    
    def get_genres(self) -> List[Dict[str, Any]]:
        """Get genre statistics"""
        return self.repository.get_genre_stats()
    
    # ============ MÉTODOS PARA GRÁFICOS ============
    def get_genre_distribution(self) -> Dict[str, Any]:
        """Get data for genre distribution chart"""
        genres = self.repository.get_genre_stats()
        return {
            "labels": [g["genre_name"] for g in genres[:10]],
            "datasets": [{
                "label": "Total de Filmes",
                "data": [g["total_movies"] for g in genres[:10]],
            }]
        }
    
    def get_movies_by_decade(self) -> Dict[str, Any]:
        """Get movies grouped by decade"""
        data = self.repository.get_movies_by_decade()
        return {
            "labels": [str(int(d["decade"])) + "s" for d in data],
            "datasets": [{
                "label": "Filmes Lançados",
                "data": [d["count"] for d in data],
            }]
        }
    
    def get_rating_distribution(self) -> Dict[str, Any]:
        """Get rating distribution"""
        data = self.repository.get_rating_distribution()
        return {
            "labels": [d['rating_range'] for d in data],
            "datasets": [{
                "label": "Número de Filmes",
                "data": [d["count"] for d in data],
            }]
        }