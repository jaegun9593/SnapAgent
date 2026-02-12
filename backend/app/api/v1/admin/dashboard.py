"""
Admin dashboard API endpoints - summary, timeseries, by-user.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, DBSession
from app.schemas.dashboard import (
    AdminDashboardSummary,
    TimeseriesResponse,
    UserUsageResponse,
)
from app.services.usage_service import UsageService


router = APIRouter(prefix="/dashboard", tags=["Admin - Dashboard"])


@router.get("/summary", response_model=AdminDashboardSummary)
async def get_admin_summary(
    admin_user: AdminUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """Get overall usage summary statistics (admin only)."""
    service = UsageService(db)
    summary = await service.get_admin_summary(
        start_date=start_date, end_date=end_date
    )
    return summary


@router.get("/usage/timeseries", response_model=TimeseriesResponse)
async def get_admin_timeseries(
    admin_user: AdminUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """Get overall usage timeseries data (admin only)."""
    service = UsageService(db)
    data = await service.get_admin_timeseries(
        start_date=start_date, end_date=end_date
    )
    return data


@router.get("/usage/by-user", response_model=UserUsageResponse)
async def get_by_user(
    admin_user: AdminUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """Get usage breakdown by user (admin only)."""
    service = UsageService(db)
    data = await service.get_admin_by_user(
        start_date=start_date, end_date=end_date
    )
    return data
