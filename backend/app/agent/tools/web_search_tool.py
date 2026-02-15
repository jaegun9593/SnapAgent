"""
DuckDuckGo web search tool for real-time information retrieval.
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)

# Backends to try in order (lite is more reliable against rate limits)
_BACKENDS = ["lite", "api", "html"]


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

        Tries multiple backends (lite → api → html) to handle rate limits.

        Args:
            query: The search query
            config: Configuration with max_results

        Returns:
            Dict with content string and results list
        """
        max_results = (config or {}).get("max_results", 5)

        from duckduckgo_search import DDGS
        from duckduckgo_search.exceptions import RatelimitException

        last_error = None

        for backend in _BACKENDS:
            try:
                results_list = []  # type: List[Dict[str, Any]]
                content_parts = []  # type: List[str]

                with DDGS() as ddgs:
                    search_results = list(
                        ddgs.text(query, max_results=max_results, backend=backend)
                    )

                    for result in search_results:
                        result_data = {
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                        }
                        results_list.append(result_data)
                        content_parts.append(
                            f"**{result_data['title']}**\n"
                            f"{result_data['snippet']}\n"
                            f"Source: {result_data['url']}"
                        )

                content = (
                    "\n\n---\n\n".join(content_parts)
                    if content_parts
                    else "No search results found"
                )
                return {"content": content, "results": results_list}

            except RatelimitException:
                logger.warning("DDG rate limit on backend=%s, trying next", backend)
                last_error = "Rate limited on all backends"
                time.sleep(0.5)
                continue
            except Exception as e:
                logger.error("Web search error (backend=%s): %s", backend, e)
                last_error = str(e)
                continue

        return {
            "content": f"Web search failed: {last_error}",
            "results": [],
        }
