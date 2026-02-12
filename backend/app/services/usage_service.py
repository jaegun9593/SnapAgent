"""
Usage service for dashboard analytics.
"""
import logging
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Agent, UsageLog, User
from app.schemas.dashboard import (
    AdminDashboardSummary,
    AgentUsage,
    AgentUsageResponse,
    DashboardSummary,
    PeriodInfo,
    TimeseriesDataPoint,
    TimeseriesResponse,
    UserUsage,
    UserUsageResponse,
)

logger = logging.getLogger(__name__)


class UsageService:
    """Service for usage analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_period(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> tuple:
        """Get date range with defaults."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        return start_date, end_date

    async def get_user_summary(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        agent_id: Optional[UUID] = None,
    ) -> DashboardSummary:
        """Get usage summary for a user."""
        start, end = self._get_period(start_date, end_date)

        query = select(
            func.count(UsageLog.id).label("total_calls"),
            func.coalesce(func.sum(UsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(UsageLog.completion_tokens), 0).label("completion_tokens"),
            func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(UsageLog.cost), 0).label("total_cost"),
            func.coalesce(func.avg(UsageLog.latency_ms), 0).label("avg_latency"),
        ).where(
            UsageLog.user_email == user.email,
            cast(UsageLog.created_at, Date) >= start,
            cast(UsageLog.created_at, Date) <= end,
        )

        if agent_id:
            query = query.where(UsageLog.agent_id == agent_id)

        result = await self.db.execute(query)
        row = result.one()

        # Count agents
        agent_result = await self.db.execute(
            select(func.count(Agent.id)).where(
                Agent.user_email == user.email, Agent.use_yn == "Y"
            )
        )
        agent_count = agent_result.scalar() or 0

        return DashboardSummary(
            total_calls=row.total_calls,
            total_prompt_tokens=row.prompt_tokens,
            total_completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            total_cost=float(row.total_cost),
            avg_latency_ms=int(row.avg_latency),
            agent_count=agent_count,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )

    async def get_user_timeseries(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        agent_id: Optional[UUID] = None,
    ) -> TimeseriesResponse:
        """Get daily usage timeseries for a user."""
        start, end = self._get_period(start_date, end_date)

        query = (
            select(
                cast(UsageLog.created_at, Date).label("date"),
                func.count(UsageLog.id).label("calls"),
                func.coalesce(func.sum(UsageLog.prompt_tokens), 0).label("prompt_tokens"),
                func.coalesce(func.sum(UsageLog.completion_tokens), 0).label(
                    "completion_tokens"
                ),
                func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
                func.coalesce(func.sum(UsageLog.cost), 0).label("cost"),
            )
            .where(
                UsageLog.user_email == user.email,
                cast(UsageLog.created_at, Date) >= start,
                cast(UsageLog.created_at, Date) <= end,
            )
            .group_by(cast(UsageLog.created_at, Date))
            .order_by(cast(UsageLog.created_at, Date))
        )

        if agent_id:
            query = query.where(UsageLog.agent_id == agent_id)

        result = await self.db.execute(query)
        rows = result.all()

        data = [
            TimeseriesDataPoint(
                date=str(row.date),
                calls=row.calls,
                prompt_tokens=row.prompt_tokens,
                completion_tokens=row.completion_tokens,
                total_tokens=row.total_tokens,
                cost=float(row.cost),
            )
            for row in rows
        ]

        return TimeseriesResponse(
            data=data,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )

    async def get_user_by_agent(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AgentUsageResponse:
        """Get usage breakdown by agent for a user."""
        start, end = self._get_period(start_date, end_date)

        query = (
            select(
                UsageLog.agent_id,
                func.count(UsageLog.id).label("calls"),
                func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
                func.coalesce(func.sum(UsageLog.cost), 0).label("cost"),
            )
            .where(
                UsageLog.user_email == user.email,
                cast(UsageLog.created_at, Date) >= start,
                cast(UsageLog.created_at, Date) <= end,
                UsageLog.agent_id.isnot(None),
            )
            .group_by(UsageLog.agent_id)
        )

        result = await self.db.execute(query)
        rows = result.all()

        data = []
        for row in rows:
            # Get agent name
            agent_result = await self.db.execute(
                select(Agent.name).where(Agent.id == row.agent_id)
            )
            agent_name = agent_result.scalar() or "Unknown"

            data.append(
                AgentUsage(
                    agent_id=str(row.agent_id),
                    agent_name=agent_name,
                    calls=row.calls,
                    total_tokens=row.total_tokens,
                    cost=float(row.cost),
                )
            )

        return AgentUsageResponse(
            data=data,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )

    async def get_admin_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AdminDashboardSummary:
        """Get overall usage summary (admin only)."""
        start, end = self._get_period(start_date, end_date)

        query = select(
            func.count(UsageLog.id).label("total_calls"),
            func.coalesce(func.sum(UsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(UsageLog.completion_tokens), 0).label("completion_tokens"),
            func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(UsageLog.cost), 0).label("total_cost"),
            func.coalesce(func.avg(UsageLog.latency_ms), 0).label("avg_latency"),
        ).where(
            cast(UsageLog.created_at, Date) >= start,
            cast(UsageLog.created_at, Date) <= end,
        )

        result = await self.db.execute(query)
        row = result.one()

        # Count users
        user_result = await self.db.execute(
            select(func.count(User.email)).where(User.use_yn == "Y", User.is_active == True)
        )
        total_users = user_result.scalar() or 0

        # Count agents
        agent_result = await self.db.execute(
            select(func.count(Agent.id)).where(Agent.use_yn == "Y")
        )
        agent_count = agent_result.scalar() or 0

        return AdminDashboardSummary(
            total_calls=row.total_calls,
            total_prompt_tokens=row.prompt_tokens,
            total_completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            total_cost=float(row.total_cost),
            avg_latency_ms=int(row.avg_latency),
            agent_count=agent_count,
            total_users=total_users,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )

    async def get_admin_timeseries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> TimeseriesResponse:
        """Get overall usage timeseries (admin only)."""
        start, end = self._get_period(start_date, end_date)

        query = (
            select(
                cast(UsageLog.created_at, Date).label("date"),
                func.count(UsageLog.id).label("calls"),
                func.coalesce(func.sum(UsageLog.prompt_tokens), 0).label("prompt_tokens"),
                func.coalesce(func.sum(UsageLog.completion_tokens), 0).label(
                    "completion_tokens"
                ),
                func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
                func.coalesce(func.sum(UsageLog.cost), 0).label("cost"),
            )
            .where(
                cast(UsageLog.created_at, Date) >= start,
                cast(UsageLog.created_at, Date) <= end,
            )
            .group_by(cast(UsageLog.created_at, Date))
            .order_by(cast(UsageLog.created_at, Date))
        )

        result = await self.db.execute(query)
        rows = result.all()

        data = [
            TimeseriesDataPoint(
                date=str(row.date),
                calls=row.calls,
                prompt_tokens=row.prompt_tokens,
                completion_tokens=row.completion_tokens,
                total_tokens=row.total_tokens,
                cost=float(row.cost),
            )
            for row in rows
        ]

        return TimeseriesResponse(
            data=data,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )

    async def get_admin_by_user(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> UserUsageResponse:
        """Get usage breakdown by user (admin only)."""
        start, end = self._get_period(start_date, end_date)

        query = (
            select(
                UsageLog.user_email,
                func.count(UsageLog.id).label("calls"),
                func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
                func.coalesce(func.sum(UsageLog.cost), 0).label("cost"),
            )
            .where(
                cast(UsageLog.created_at, Date) >= start,
                cast(UsageLog.created_at, Date) <= end,
            )
            .group_by(UsageLog.user_email)
        )

        result = await self.db.execute(query)
        rows = result.all()

        data = [
            UserUsage(
                user_email=row.user_email,
                calls=row.calls,
                total_tokens=row.total_tokens,
                cost=float(row.cost),
            )
            for row in rows
        ]

        return UserUsageResponse(
            data=data,
            period=PeriodInfo(start_date=str(start), end_date=str(end)),
        )
