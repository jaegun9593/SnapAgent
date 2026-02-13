"""
Token-limit middleware — checks the user's token/API-call budget before a run.

Queries *token_limits* (per-user or global) and *usage_logs* to determine
whether the user has exceeded their daily / monthly / total allowance.
If any active limit is breached the context is aborted.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.middleware.base import AgentContext, AgentMiddleware
from app.db.models import TokenLimit, UsageLog

logger = logging.getLogger(__name__)

_PERIOD_DELTAS = {
    "per_minute": timedelta(minutes=1),
    "per_hour": timedelta(hours=1),
    "per_day": timedelta(days=1),
    "daily": timedelta(days=1),
    "monthly": timedelta(days=30),
}


class TokenLimitMiddleware(AgentMiddleware):
    """Abort the run if the user has exceeded any active token / API-call limit."""

    async def before_run(self, ctx: AgentContext) -> AgentContext:
        db: AsyncSession = ctx.db
        email = ctx.user.email

        # Fetch active limits: user-specific first, then global (user_email IS NULL)
        result = await db.execute(
            select(TokenLimit).where(
                TokenLimit.is_active == True,
                TokenLimit.use_yn == "Y",
                or_(
                    TokenLimit.user_email == email,
                    TokenLimit.user_email.is_(None),
                ),
            )
        )
        limits = result.scalars().all()

        if not limits:
            return ctx

        now = datetime.now(timezone.utc)

        for limit in limits:
            delta = _PERIOD_DELTAS.get(limit.limit_type)
            since: Optional[datetime] = now - delta if delta else None

            # Build usage aggregation query
            usage_q = select(
                func.coalesce(func.sum(UsageLog.total_tokens), 0).label("sum_tokens"),
                func.count(UsageLog.id).label("api_calls"),
            ).where(UsageLog.user_email == email)

            if since is not None:
                usage_q = usage_q.where(UsageLog.created_at >= since)

            row = (await db.execute(usage_q)).one()
            used_tokens: int = int(row.sum_tokens)
            api_calls: int = int(row.api_calls)

            # Check token cap
            if limit.max_tokens and used_tokens >= limit.max_tokens:
                period_label = self._period_label(limit.limit_type)
                ctx.aborted = True
                ctx.abort_reason = (
                    f"{period_label} 토큰 사용량을 초과했습니다. "
                    f"(사용: {used_tokens:,} / 제한: {limit.max_tokens:,})"
                )
                return ctx

            # Check API call cap
            if limit.max_api_calls and api_calls >= limit.max_api_calls:
                period_label = self._period_label(limit.limit_type)
                ctx.aborted = True
                ctx.abort_reason = (
                    f"{period_label} API 호출 횟수를 초과했습니다. "
                    f"(호출: {api_calls:,} / 제한: {limit.max_api_calls:,})"
                )
                return ctx

        return ctx

    @staticmethod
    def _period_label(limit_type: str) -> str:
        labels = {
            "per_minute": "분당",
            "per_hour": "시간당",
            "per_day": "일일",
            "daily": "일일",
            "monthly": "월간",
            "total": "전체",
        }
        return labels.get(limit_type, limit_type)
