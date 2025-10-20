import os
from pathlib import Path
from dotenv import load_dotenv

# Forçar reload do .env
load_dotenv(override=True)

class Settings:
    """Configurações centralizadas do projeto."""
    
    # Diretórios
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "moviesdb")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    
    @property
    def postgres_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Buckets MinIO
    BUCKET_BRONZE_MOVIELENS = "bronze-movielens"
    BUCKET_BRONZE_TMDB = "bronze-tmdb"
    BUCKET_SILVER_MOVIELENS = "silver-movielens"
    BUCKET_SILVER_TMDB = "silver-tmdb"
    BUCKET_GOLD_MOVIELENS = "gold-movielens"
    BUCKET_GOLD_TMDB = "gold-tmdb"
    
    # TMDB API - CORRIGIDO!
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "3de71fe2ca3968fb01bf2892e3a2ecab")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_IMAGE_BASE_URL = os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p/")
    
    # Rate Limiting TMDB
    TMDB_MAX_REQUESTS_PER_SECOND = 4
    TMDB_BATCH_SIZE = 100
    TMDB_RETRY_ATTEMPTS = 3
    
    # Schemas PostgreSQL
    SCHEMA_SILVER_MOVIELENS = "silver"
    SCHEMA_SILVER_TMDB = "silver_tmdb"
    SCHEMA_GOLD_MOVIELENS = "gold"
    SCHEMA_GOLD_TMDB = "gold_tmdb"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Singleton
settings = Settings()

# Debug: Verificar se API key foi carregada
if __name__ == "__main__":
    print(f"TMDB_API_KEY: {settings.TMDB_API_KEY[:10]}...")  # Mostrar só os primeiros 10 caracteres
    print(f"TMDB_BASE_URL: {settings.TMDB_BASE_URL}")