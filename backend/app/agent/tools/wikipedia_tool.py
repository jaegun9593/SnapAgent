"""
Wikipedia search tool for encyclopedia article retrieval.
"""
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class WikipediaTool(BaseTool):
    """Wikipedia article search tool."""

    @property
    def name(self) -> str:
        return "wikipedia"

    @property
    def description(self) -> str:
        return "Search Wikipedia for encyclopedia articles"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search Wikipedia articles.

        Args:
            query: The search query
            config: Configuration with lang, max_results

        Returns:
            Dict with content string and results list
        """
        config = config or {}
        lang = config.get("lang", "ko")
        max_results = config.get("max_results", 3)

        try:
            results_list: List[Dict[str, Any]] = []
            content_parts: List[str] = []

            # Step 1: Search for matching articles
            search_url = f"https://{lang}.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
                "utf8": 1,
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(search_url, params=search_params)
                resp.raise_for_status()
                search_data = resp.json()

                search_results = search_data.get("query", {}).get("search", [])

                # Step 2: Get summary for each article
                for item in search_results:
                    title = item.get("title", "")
                    page_id = item.get("pageid", 0)

                    # Fetch page summary via REST API
                    summary_url = (
                        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                        f"{title.replace(' ', '_')}"
                    )
                    try:
                        summary_resp = await client.get(summary_url)
                        if summary_resp.status_code == 200:
                            summary_data = summary_resp.json()
                            extract = summary_data.get("extract", "")
                            page_url = summary_data.get("content_urls", {}).get(
                                "desktop", {}
                            ).get("page", f"https://{lang}.wikipedia.org/wiki/{title}")
                        else:
                            extract = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                            page_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    except Exception:
                        extract = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                        page_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"

                    result_data = {
                        "title": title,
                        "url": page_url,
                        "snippet": extract[:500] if extract else "",
                        "page_id": page_id,
                    }
                    results_list.append(result_data)
                    content_parts.append(
                        f"**{title}**\n"
                        f"{extract[:500]}\n"
                        f"Source: {page_url}"
                    )

            content = (
                "\n\n---\n\n".join(content_parts)
                if content_parts
                else "Wikipedia에서 관련 문서를 찾지 못했습니다."
            )
            return {"content": content, "results": results_list}

        except Exception as e:
            logger.error("Wikipedia search error: %s", e)
            return {
                "content": f"Wikipedia search failed: {str(e)}",
                "results": [],
            }
