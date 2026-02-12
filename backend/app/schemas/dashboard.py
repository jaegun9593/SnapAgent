"""
Dashboard schemas for usage analytics.
"""
from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PeriodInfo(BaseModel):
    """Time period information."""

    start_date: str
    end_date: str


class DashboardSummary(BaseModel):
    """Dashboard summary statistics for a user."""

    total_calls: int = Field(description="Total API calls")
    total_prompt_tokens: int = Field(description="Total input tokens")
    total_completion_tokens: int = Field(description="Total output tokens")
    total_tokens: int = Field(description="Total tokens (input + output)")
    total_cost: float = Field(description="Estimated total cost in USD")
    avg_latency_ms: int = Field(description="Average latency in milliseconds")
    agent_count: int = Field(description="Number of agents")
    period: PeriodInfo = Field(description="Time period for the summary")


class AdminDashboardSummary(DashboardSummary):
    """Admin dashboard summary - includes user count."""

    total_users: int = Field(description="Total number of users")


class TimeseriesDataPoint(BaseModel):
    """Single data point in timeseries."""

    date: str = Field(description="Date in ISO format")
    calls: int = Field(description="Number of API calls")
    prompt_tokens: int = Field(description="Input tokens")
    completion_tokens: int = Field(description="Output tokens")
    total_tokens: int = Field(description="Total tokens")
    cost: float = Field(description="Estimated cost in USD")


class TimeseriesResponse(BaseModel):
    """Timeseries data response."""

    data: List[TimeseriesDataPoint]
    period: PeriodInfo


class AgentUsage(BaseModel):
    """Usage statistics for a single agent."""

    agent_id: str
    agent_name: str
    calls: int
    total_tokens: int
    cost: float


class AgentUsageResponse(BaseModel):
    """Agent usage breakdown response."""

    data: List[AgentUsage]
    period: PeriodInfo


class UserUsage(BaseModel):
    """Usage statistics for a single user (admin view)."""

    user_email: str
    calls: int
    total_tokens: int
    cost: float


class UserUsageResponse(BaseModel):
    """User usage breakdown response (admin view)."""

    data: List[UserUsage]
    period: PeriodInfo


class DashboardQueryParams(BaseModel):
    """Common query parameters for dashboard endpoints."""

    start_date: Optional[date] = Field(
        default=None,
        description="Start date for filtering (default: 30 days ago)",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="End date for filtering (default: today)",
    )
    agent_id: Optional[UUID] = Field(
        default=None,
        description="Filter by specific agent",
    )
