"""
Structured-logging middleware — records timing and summary info for every
lifecycle hook so that ops can trace agent runs end-to-end.

Timing data is also stored in ``ctx.metadata["timings"]`` for downstream
consumption (e.g. SSE events, usage logs).
"""
import logging
import time
from typing import Any, Dict, List

from app.agent.middleware.base import AgentContext, AgentMiddleware

logger = logging.getLogger("agent.middleware.logging")


class LoggingMiddleware(AgentMiddleware):
    """Log each lifecycle phase with structured context."""

    async def before_run(self, ctx: AgentContext) -> AgentContext:
        ctx.metadata.setdefault("timings", {})
        ctx.metadata["_run_start"] = time.monotonic()
        logger.info(
            "[Agent %s] Run start | user=%s query_len=%d",
            ctx.agent.id,
            ctx.user.email,
            len(ctx.query),
        )
        return ctx

    async def before_tool(
        self, tool_name: str, query: str, ctx: AgentContext
    ) -> AgentContext:
        ctx.metadata[f"_tool_{tool_name}_start"] = time.monotonic()
        logger.info(
            "[Agent %s] Tool start | tool=%s query_len=%d",
            ctx.agent.id,
            tool_name,
            len(query),
        )
        return ctx

    async def after_tool(
        self, tool_name: str, result: Dict[str, Any], ctx: AgentContext
    ) -> AgentContext:
        start = ctx.metadata.pop(f"_tool_{tool_name}_start", None)
        elapsed_ms = int((time.monotonic() - start) * 1000) if start else 0
        ctx.metadata["timings"][f"tool_{tool_name}"] = elapsed_ms
        logger.info(
            "[Agent %s] Tool done  | tool=%s elapsed=%dms success=%s",
            ctx.agent.id,
            tool_name,
            elapsed_ms,
            result.get("success", "?"),
        )
        return ctx

    async def before_llm(
        self, messages: List[Dict[str, str]], ctx: AgentContext
    ) -> AgentContext:
        ctx.metadata["_llm_start"] = time.monotonic()
        logger.info(
            "[Agent %s] LLM start  | messages=%d",
            ctx.agent.id,
            len(messages),
        )
        return ctx

    async def after_llm(self, response: str, ctx: AgentContext) -> AgentContext:
        start = ctx.metadata.pop("_llm_start", None)
        elapsed_ms = int((time.monotonic() - start) * 1000) if start else 0
        ctx.metadata["timings"]["llm"] = elapsed_ms
        logger.info(
            "[Agent %s] LLM done   | elapsed=%dms response_len=%d",
            ctx.agent.id,
            elapsed_ms,
            len(response),
        )
        return ctx

    async def on_error(
        self, error: Exception, step: str, ctx: AgentContext
    ) -> None:
        logger.error(
            "[Agent %s] Error in %s | %s: %s",
            ctx.agent.id,
            step,
            type(error).__name__,
            error,
        )

    async def after_run(self, ctx: AgentContext) -> None:
        start = ctx.metadata.pop("_run_start", None)
        total_ms = int((time.monotonic() - start) * 1000) if start else 0
        ctx.metadata["timings"]["total"] = total_ms
        logger.info(
            "[Agent %s] Run done   | total=%dms aborted=%s timings=%s",
            ctx.agent.id,
            total_ms,
            ctx.aborted,
            ctx.metadata.get("timings"),
        )
