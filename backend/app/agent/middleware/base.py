"""
Base middleware classes for the ReAct Agent pipeline.

Provides AgentContext (shared state), AgentMiddleware (ABC with lifecycle hooks),
and MiddlewareChain (sequential executor).
"""
import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Agent, User

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared execution context passed through the middleware chain."""

    query: str
    user: User
    agent: Agent
    db: AsyncSession
    metadata: Dict[str, Any] = field(default_factory=dict)
    aborted: bool = False
    abort_reason: str = ""


class AgentMiddleware(ABC):
    """Base class for agent middlewares. Override only the hooks you need."""

    async def before_run(self, ctx: AgentContext) -> AgentContext:
        return ctx

    async def before_tool(
        self, tool_name: str, query: str, ctx: AgentContext
    ) -> AgentContext:
        return ctx

    async def after_tool(
        self, tool_name: str, result: Dict[str, Any], ctx: AgentContext
    ) -> AgentContext:
        return ctx

    async def before_llm(
        self, messages: List[Dict[str, str]], ctx: AgentContext
    ) -> AgentContext:
        return ctx

    async def after_llm(self, response: str, ctx: AgentContext) -> AgentContext:
        return ctx

    async def on_error(
        self, error: Exception, step: str, ctx: AgentContext
    ) -> None:
        pass

    async def after_run(self, ctx: AgentContext) -> None:
        pass


class MiddlewareChain:
    """Executes a list of middlewares sequentially, respecting abort signals."""

    def __init__(self, middlewares: Optional[List[AgentMiddleware]] = None):
        self._middlewares: List[AgentMiddleware] = middlewares or []

    def add(self, mw: AgentMiddleware) -> None:
        self._middlewares.append(mw)

    async def run_before_run(self, ctx: AgentContext) -> AgentContext:
        for mw in self._middlewares:
            if ctx.aborted:
                break
            try:
                ctx = await mw.before_run(ctx)
            except Exception as exc:
                logger.error("Middleware %s.before_run failed: %s", type(mw).__name__, exc)
                await self._propagate_error(exc, "before_run", ctx)
        return ctx

    async def run_before_tool(
        self, tool_name: str, query: str, ctx: AgentContext
    ) -> AgentContext:
        for mw in self._middlewares:
            if ctx.aborted:
                break
            try:
                ctx = await mw.before_tool(tool_name, query, ctx)
            except Exception as exc:
                logger.error("Middleware %s.before_tool failed: %s", type(mw).__name__, exc)
                await self._propagate_error(exc, "before_tool", ctx)
        return ctx

    async def run_after_tool(
        self, tool_name: str, result: Dict[str, Any], ctx: AgentContext
    ) -> AgentContext:
        for mw in self._middlewares:
            if ctx.aborted:
                break
            try:
                ctx = await mw.after_tool(tool_name, result, ctx)
            except Exception as exc:
                logger.error("Middleware %s.after_tool failed: %s", type(mw).__name__, exc)
                await self._propagate_error(exc, "after_tool", ctx)
        return ctx

    async def run_before_llm(
        self, messages: List[Dict[str, str]], ctx: AgentContext
    ) -> AgentContext:
        for mw in self._middlewares:
            if ctx.aborted:
                break
            try:
                ctx = await mw.before_llm(messages, ctx)
            except Exception as exc:
                logger.error("Middleware %s.before_llm failed: %s", type(mw).__name__, exc)
                await self._propagate_error(exc, "before_llm", ctx)
        return ctx

    async def run_after_llm(self, response: str, ctx: AgentContext) -> AgentContext:
        for mw in self._middlewares:
            if ctx.aborted:
                break
            try:
                ctx = await mw.after_llm(response, ctx)
            except Exception as exc:
                logger.error("Middleware %s.after_llm failed: %s", type(mw).__name__, exc)
                await self._propagate_error(exc, "after_llm", ctx)
        return ctx

    async def run_on_error(
        self, error: Exception, step: str, ctx: AgentContext
    ) -> None:
        for mw in self._middlewares:
            try:
                await mw.on_error(error, step, ctx)
            except Exception as exc:
                logger.error("Middleware %s.on_error failed: %s", type(mw).__name__, exc)

    async def run_after_run(self, ctx: AgentContext) -> None:
        for mw in self._middlewares:
            try:
                await mw.after_run(ctx)
            except Exception as exc:
                logger.error("Middleware %s.after_run failed: %s", type(mw).__name__, exc)

    async def _propagate_error(
        self, error: Exception, step: str, ctx: AgentContext
    ) -> None:
        """Notify all middlewares about an error that occurred in the chain."""
        await self.run_on_error(error, step, ctx)
