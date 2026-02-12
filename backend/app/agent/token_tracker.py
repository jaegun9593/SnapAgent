"""
Token usage tracker for recording per-request usage.
"""
import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Agent, UsageLog, User

logger = logging.getLogger(__name__)


class TokenTracker:
    """Track token usage and cost per request."""

    def __init__(self, db: AsyncSession, user: User, agent: Agent):
        self.db = db
        self.user = user
        self.agent = agent

    async def track(
        self,
        usage: Dict[str, int],
        model_id: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ) -> None:
        """
        Record token usage to the database.

        Args:
            usage: Dict with prompt_tokens, completion_tokens, total_tokens
            model_id: The model identifier used
            latency_ms: Request latency in milliseconds
        """
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        # Estimate cost (rough pricing: $0.01 per 1K tokens)
        cost = Decimal(str(total_tokens)) / Decimal("1000") * Decimal("0.01")

        log = UsageLog(
            user_email=self.user.email,
            agent_id=self.agent.id,
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            latency_ms=latency_ms,
        )
        self.db.add(log)
        await self.db.commit()
