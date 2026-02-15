"""
Tool executor for running agent tools and returning results.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Agent, AgentTool, User

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Execute agent tools and return results."""

    def __init__(self, db: AsyncSession, agent: Agent, user: User):
        self.db = db
        self.agent = agent
        self.user = user

    async def get_enabled_tools(self) -> List[AgentTool]:
        """Get all enabled tools for the agent."""
        result = await self.db.execute(
            select(AgentTool)
            .where(
                AgentTool.agent_id == self.agent.id,
                AgentTool.use_yn == "Y",
                AgentTool.is_enabled == True,
            )
            .order_by(AgentTool.sort_order)
        )
        return list(result.scalars().all())

    async def execute(
        self,
        tool: AgentTool,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a tool and return its result.

        Args:
            tool: The tool to execute
            query: The query to pass to the tool
            context: Previous tool results for context

        Returns:
            Dict with tool_type, output, and metadata
        """
        try:
            # RAG tool needs special DB/Agent/User context
            if tool.tool_type == "rag":
                return await self._execute_rag(query, tool.tool_config)

            # All other tools: look up via registry
            from app.agent.tools.registry import get_tool_class

            tool_cls = get_tool_class(tool.tool_type)
            if tool_cls is None:
                return {
                    "tool_type": tool.tool_type,
                    "output": f"Unknown tool type: {tool.tool_type}",
                    "success": False,
                }

            tool_instance = tool_cls()
            result = await tool_instance.execute(query, config=tool.tool_config)

            return {
                "tool_type": tool.tool_type,
                "output": result.get("content", ""),
                "success": True,
                **{k: v for k, v in result.items() if k != "content"},
            }

        except Exception as e:
            logger.error(f"Tool execution error ({tool.tool_type}): {e}")
            return {
                "tool_type": tool.tool_type,
                "output": f"Tool execution failed: {str(e)}",
                "success": False,
                "error": str(e),
            }

    async def _execute_rag(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute RAG vector search."""
        from app.agent.tools.rag_tool import RAGTool

        rag_tool = RAGTool(self.db, self.agent, self.user)
        results = await rag_tool.search(query, config=config)
        return {
            "tool_type": "rag",
            "output": results.get("content", ""),
            "chunks": results.get("chunks", []),
            "success": True,
        }
