"""
Admin router aggregation.
"""
from fastapi import APIRouter

from app.api.v1.admin import models, dashboard, token_limits

admin_router = APIRouter(tags=["Admin"])

admin_router.include_router(models.router)
admin_router.include_router(dashboard.router)
admin_router.include_router(token_limits.router)
