"""
ArXiv academic paper search tool.
"""
import logging
from typing import Any, Dict, List, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ArxivTool(BaseTool):
    """ArXiv academic paper search tool."""

    @property
    def name(self) -> str:
        return "arxiv"

    @property
    def description(self) -> str:
        return "Search ArXiv for academic papers (title, abstract, PDF)"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search ArXiv papers.

        Args:
            query: The search query
            config: Configuration with max_results

        Returns:
            Dict with content string and results list
        """
        config = config or {}
        max_results = config.get("max_results", 5)

        try:
            import arxiv

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )

            results_list: List[Dict[str, Any]] = []
            content_parts: List[str] = []

            for paper in search.results():
                authors = ", ".join(a.name for a in paper.authors[:3])
                if len(paper.authors) > 3:
                    authors += f" 외 {len(paper.authors) - 3}명"

                result_data = {
                    "title": paper.title,
                    "authors": authors,
                    "abstract": paper.summary[:300] if paper.summary else "",
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
                    "categories": [c for c in paper.categories] if paper.categories else [],
                }
                results_list.append(result_data)
                content_parts.append(
                    f"**{paper.title}**\n"
                    f"Authors: {authors}\n"
                    f"Published: {result_data['published']}\n"
                    f"{paper.summary[:300]}...\n"
                    f"PDF: {paper.pdf_url}"
                )

            content = (
                "\n\n---\n\n".join(content_parts)
                if content_parts
                else "ArXiv에서 관련 논문을 찾지 못했습니다."
            )
            return {"content": content, "results": results_list}

        except Exception as e:
            logger.error("ArXiv search error: %s", e)
            return {
                "content": f"ArXiv search failed: {str(e)}",
                "results": [],
            }
