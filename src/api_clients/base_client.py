from abc import ABC, abstractmethod
import requests
import time
from typing import Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAPIClient(ABC):
    """Classe base abstrata para clientes de API."""
    
    def __init__(self, base_url: str, api_key: str, rate_limit: float = 0.25):
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self._setup_session()
    
    @abstractmethod
    def _setup_session(self):
        """Configura headers e autenticação da sessão."""
        pass
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict:
        """Faz requisição HTTP com rate limiting e retry."""
        url = f"{self.base_url}/{endpoint}"
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.request(method, url, params=params)
                response.raise_for_status()
                
                # Rate limiting
                time.sleep(self.rate_limit)
                
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limit atingido. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                logger.error(f"Erro HTTP {response.status_code}: {e}")
                if attempt == retries - 1:
                    raise
            
            except Exception as e:
                logger.error(f"Erro na requisição (tentativa {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    return {}
                time.sleep(2 ** attempt)
        
        return {}