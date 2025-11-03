import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar rotas corretamente
from api.routes import movielens, tmdb, analytics

app = FastAPI(
    title="🎬 DataFlix API",
    description="API para análise de dados de filmes (MovieLens + TMDB)",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(movielens.router)
app.include_router(tmdb.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    """Endpoint raiz - informações da API"""
    return {
        "message": "🎬 Bem-vindo à DataFlix API!",
        "version": "1.0.0",
        "endpoints": {
            "movielens": "/movielens/",
            "tmdb": "/tmdb/",
            "analytics": "/analytics/",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Verificar se a API está funcionando"""
    return {"status": "ok", "service": "DataFlix API"}