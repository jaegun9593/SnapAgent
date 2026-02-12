"""
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.api.v1.admin.router import admin_router
from app.config import settings
from app.core.exceptions import AppException
from app.db.database import async_session_maker
from app.services.template_seed import seed_system_templates

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: seed system templates
    try:
        async with async_session_maker() as db:
            await seed_system_templates(db)
    except Exception:
        logger.exception("Failed to seed system templates (server continues)")
    yield


# Create FastAPI app
app = FastAPI(
    title="SnapAgent API",
    description="RAG Agent Builder Platform Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {},
            },
        },
    )


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "SnapAgent API",
        "version": "0.1.0",
        "environment": settings.environment,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


# Include API v1 router (user-facing)
app.include_router(api_router, prefix="/api/v1")

# Include Admin router
app.include_router(admin_router, prefix="/api/v1/admin")
