"""
DataFlix Analytics API
FastAPI application for movie analytics
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
from contextlib import asynccontextmanager

from .config import settings
from .database import test_connection
from .routes import (
    health_router,
    movielens_router,
    tmdb_router,
    box_office_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info("🚀 Starting DataFlix Analytics API...")
    logger.info(f"📊 Version: {settings.VERSION}")
    logger.info(f"🔧 Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Test database connection
    if test_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.warning("⚠️ Database connection failed - some endpoints may not work")
    
    logger.info("✅ API is ready to serve requests")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DataFlix Analytics API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for comprehensive movie analytics across MovieLens, TMDB, and Box Office data",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============ CORS CONFIGURATION - MAIS PERMISSIVO ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"],  # Expõe todos os headers
    max_age=3600,  # Cache de preflight por 1 hora
)

# Include routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(movielens_router, prefix=settings.API_V1_PREFIX)
app.include_router(tmdb_router, prefix=settings.API_V1_PREFIX)
app.include_router(box_office_router, prefix=settings.API_V1_PREFIX)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "endpoints": {
            "movielens": f"{settings.API_V1_PREFIX}/movielens/analytics",
            "tmdb": f"{settings.API_V1_PREFIX}/tmdb/analytics",
            "box_office": f"{settings.API_V1_PREFIX}/box-office/analytics"
        }
    }

# Validation error handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors() if settings.DEBUG else "Invalid data format"
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc) if settings.DEBUG else "An unexpected error occurred"
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )