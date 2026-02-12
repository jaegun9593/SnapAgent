"""
User dashboard API endpoints - summary, timeseries, by-agent.
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.dashboard import (
    DashboardSummary,
    TimeseriesResponse,
    AgentUsageResponse,
)
from app.services.usage_service import UsageService


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: CurrentUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    agent_id: Optional[UUID] = Query(None),
):
    """Get usage summary statistics for the current user."""
    service = UsageService(db)
    summary = await service.get_user_summary(
        current_user, start_date=start_date, end_date=end_date, agent_id=agent_id
    )
    return summary


@router.get("/usage/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    current_user: CurrentUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    agent_id: Optional[UUID] = Query(None),
):
    """Get usage timeseries data for the current user."""
    service = UsageService(db)
    data = await service.get_user_timeseries(
        current_user, start_date=start_date, end_date=end_date, agent_id=agent_id
    )
    return data


@router.get("/usage/by-agent", response_model=AgentUsageResponse)
async def get_by_agent(
    current_user: CurrentUser,
    db: DBSession,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """Get usage breakdown by agent for the current user."""
    service = UsageService(db)
    data = await service.get_user_by_agent(
        current_user, start_date=start_date, end_date=end_date
    )
    return data
