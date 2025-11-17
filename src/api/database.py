"""
Database connection management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Engine com pool de conexões
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Testa conexão antes de usar
    pool_size=10,            # Número de conexões no pool
    max_overflow=20,         # Conexões extras permitidas
    echo=settings.DEBUG      # Log SQL queries em modo debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency para injetar sessão do banco nas rotas
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection() -> bool:
    """
    Testa conexão com banco
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False