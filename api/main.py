import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.database import init_db
from api.middleware import LoggingMiddleware
from api.models import ErrorResponse, HealthResponse
from api.routers import approvals, analytics, images, posts, replies


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for the application"""
    # Startup
    logger.info("Initializing Sundai API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Sundai API...")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API for Sundai Bot - AI-powered social media automation",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(replies.router, prefix="/api/v1/replies", tags=["replies"])
app.include_router(images.router, prefix="/api/v1/images", tags=["images"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(version=settings.api_version)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Sundai Bot API",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "posts": "/api/v1/posts",
            "replies": "/api/v1/replies",
            "images": "/api/v1/images",
            "analytics": "/api/v1/analytics"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return ErrorResponse(
        error="Internal Server Error",
        detail=str(exc),
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        workers=settings.workers
    )
