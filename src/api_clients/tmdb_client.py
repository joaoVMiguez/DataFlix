from typing import Dict, List, Optional
from src.api_clients.base_client import BaseAPIClient
from src.settings.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TMDBClient(BaseAPIClient):
    """Cliente para interagir com a API do TMDB."""
    
    def __init__(self):
        super().__init__(
            base_url=settings.TMDB_BASE_URL,
            api_key=settings.TMDB_API_KEY,
            rate_limit=1 / settings.TMDB_MAX_REQUESTS_PER_SECOND
        )
        logger.info("✅ TMDBClient inicializado")
    
    def _setup_session(self):
        """Configura autenticação via query parameter."""
        self.session.params = {"api_key": self.api_key}
    
    def get_movie_details(self, tmdb_id: int) -> Dict:
        """Obtém detalhes completos de um filme."""
        endpoint = f"movie/{tmdb_id}"
        params = {
            "append_to_response": "credits,keywords,videos,release_dates"
        }
        
        logger.debug(f"Buscando detalhes do filme TMDB ID: {tmdb_id}")
        return self._make_request(endpoint, params)
    
    def search_movie(self, title: str, year: Optional[int] = None) -> List[Dict]:
        """Busca filme por título e ano."""
        endpoint = "search/movie"
        params = {"query": title}
        
        if year:
            params["year"] = year
        
        logger.debug(f"Buscando: {title} ({year or 'qualquer ano'})")
        response = self._make_request(endpoint, params)
        return response.get("results", [])
    
    def get_movie_by_imdb_id(self, imdb_id: str) -> Dict:
        """Busca filme pelo ID do IMDb."""
        endpoint = f"find/{imdb_id}"
        params = {"external_source": "imdb_id"}
        
        logger.debug(f"Buscando por IMDb ID: {imdb_id}")
        response = self._make_request(endpoint, params)
        results = response.get("movie_results", [])
        
        return results[0] if results else {}
    
    def get_credits(self, tmdb_id: int) -> Dict:
        """Obtém elenco e equipe de um filme."""
        endpoint = f"movie/{tmdb_id}/credits"
        return self._make_request(endpoint)
    
    def get_poster_url(self, poster_path: str, size: str = "w500") -> str:
        """Constrói URL completa do poster."""
        if not poster_path:
            return ""
        return f"{settings.TMDB_IMAGE_BASE_URL}{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> str:
        """Constrói URL completa do backdrop."""
        if not backdrop_path:
            return ""
        return f"{settings.TMDB_IMAGE_BASE_URL}{size}{backdrop_path}"