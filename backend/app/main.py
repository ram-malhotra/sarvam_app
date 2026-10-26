"""FastAPI main application entrypoint for VoiceMenu AI."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import init_db
from app.routers import kitchen, menu, orders, qr, voice

# Configure root logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("voicemenu")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager to handle startup and shutdown routines."""
    logger.info("Starting up VoiceMenu AI Backend...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error("Failed during database initialization: %s", exc, exc_info=True)
        raise exc
    yield
    logger.info("Shutting down VoiceMenu AI Backend...")


settings = get_settings()

app = FastAPI(
    title="VoiceMenu AI API",
    description="Multilingual voice-first food ordering API powered by Sarvam AI.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(voice.router)
app.include_router(kitchen.router)
app.include_router(qr.router)


@app.get(
    "/api/health",
    summary="Health check endpoint",
    tags=["System"],
)
def health_check() -> Dict[str, str]:
    """Return system health status and service metadata.

    Returns:
        Dict[str, str]: Service status payload.
    """
    return {
        "status": "healthy",
        "service": "voicemenu-backend",
        "version": "1.0.0",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions with consistent JSON formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled runtime errors, log them securely, and prevent internal leakage."""
    logger.error("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred. Please try again later."},
    )
