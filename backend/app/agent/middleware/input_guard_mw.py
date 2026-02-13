"""
Input guard middleware — validates and normalises the user query before execution.

Checks:
- Empty / whitespace-only query → abort
- Maximum length exceeded (default 10 000 chars) → abort
- Basic normalisation: strip + collapse consecutive whitespace
"""
import re
from typing import Optional

from app.agent.middleware.base import AgentContext, AgentMiddleware

MAX_QUERY_LENGTH = 10_000


class InputGuardMiddleware(AgentMiddleware):
    """Validate and sanitise user input at the start of a run."""

    def __init__(self, max_length: Optional[int] = None):
        self._max_length = max_length or MAX_QUERY_LENGTH

    async def before_run(self, ctx: AgentContext) -> AgentContext:
        query = ctx.query

        # 1. Empty check
        if not query or not query.strip():
            ctx.aborted = True
            ctx.abort_reason = "질문을 입력해 주세요."
            return ctx

        # 2. Strip + collapse whitespace
        query = query.strip()
        query = re.sub(r"\s+", " ", query)
        ctx.query = query

        # 3. Max length check
        if len(query) > self._max_length:
            ctx.aborted = True
            ctx.abort_reason = (
                f"입력이 너무 깁니다. 최대 {self._max_length:,}자까지 허용됩니다."
            )
            return ctx

        return ctx
