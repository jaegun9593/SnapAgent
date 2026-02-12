"""
DuckDuckGo web search tool for real-time information retrieval.
"""
import logging
from typing import Any, Dict, List, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Web search tool using DuckDuckGo."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for real-time information using DuckDuckGo"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute web search."""
        return await self.search(query, config=config)

    async def search(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo.

        Args:
            query: The search query
            config: Configuration with max_results

        Returns:
            Dict with content string and results list
        """
        max_results = (config or {}).get("max_results", 5)

        try:
            from duckduckgo_search import DDGS

            results_list = []
            content_parts = []

            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=max_results))

                for result in search_results:
                    result_data = {
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    }
                    results_list.append(result_data)
                    content_parts.append(
                        f"**{result_data['title']}**\n{result_data['snippet']}\nSource: {result_data['url']}"
                    )

            content = "\n\n---\n\n".join(content_parts) if content_parts else "No search results found"

            return {"content": content, "results": results_list}

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"content": f"Web search failed: {str(e)}", "results": []}
