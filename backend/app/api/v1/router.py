"""
API v1 router - aggregates all v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    agents,
    templates,
    files,
    chat,
    dashboard,
)


# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(agents.router)
api_router.include_router(templates.router)
api_router.include_router(files.router)
api_router.include_router(chat.router)
api_router.include_router(dashboard.router)
