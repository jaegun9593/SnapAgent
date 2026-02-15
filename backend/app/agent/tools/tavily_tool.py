"""
Tavily AI-optimized search tool for high-quality web search results.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class TavilySearchTool(BaseTool):
    """Tavily AI search tool — high-quality web search results."""

    @property
    def name(self) -> str:
        return "tavily_search"

    @property
    def description(self) -> str:
        return "AI-optimized web search with high accuracy using Tavily"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Tavily search.

        Args:
            query: The search query
            config: Configuration with api_key, max_results, search_depth

        Returns:
            Dict with content string and results list
        """
        config = config or {}
        api_key = config.get("api_key") or os.getenv("TAVILY_API_KEY", "")
        max_results = config.get("max_results", 5)
        search_depth = config.get("search_depth", "basic")

        if not api_key:
            return {
                "content": "Tavily API 키가 설정되지 않았습니다. 환경변수 TAVILY_API_KEY 또는 도구 설정에서 api_key를 입력하세요.",
                "results": [],
            }

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=api_key)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
            )

            results_list: List[Dict[str, Any]] = []
            content_parts: List[str] = []

            for result in response.get("results", []):
                result_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                    "score": result.get("score", 0),
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

        except Exception as e:
            logger.error("Tavily search error: %s", e)
            return {
                "content": f"Tavily search failed: {str(e)}",
                "results": [],
            }
