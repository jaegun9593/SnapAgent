"""
Web page scraper tool for extracting text content from URLs.
"""
import logging
import re
from typing import Any, Dict, Optional

import httpx

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class WebScraperTool(BaseTool):
    """Web page text extraction tool using BeautifulSoup."""

    @property
    def name(self) -> str:
        return "web_scraper"

    @property
    def description(self) -> str:
        return "Extract text content from a web page URL"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scrape text content from a URL.

        Args:
            query: The URL to scrape
            config: Configuration with max_chars, timeout

        Returns:
            Dict with content (extracted text) and metadata
        """
        config = config or {}
        max_chars = config.get("max_chars", 5000)
        timeout = config.get("timeout", 15)
        url = query.strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            async with httpx.AsyncClient(
                timeout=float(timeout), follow_redirects=True
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script, style, nav, footer elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            # Clean up excessive whitespace
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = re.sub(r" {2,}", " ", text)

            # Truncate to max_chars
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n... (truncated)"

            # Extract page title
            title = soup.title.string.strip() if soup.title and soup.title.string else url

            return {
                "content": f"**{title}**\n\nSource: {url}\n\n{text}",
                "title": title,
                "url": url,
                "char_count": len(text),
            }

        except httpx.HTTPStatusError as e:
            logger.error("Web scraper HTTP error: %s", e)
            return {
                "content": f"페이지 접근 실패 (HTTP {e.response.status_code}): {url}",
                "title": "",
                "url": url,
                "char_count": 0,
            }
        except Exception as e:
            logger.error("Web scraper error: %s", e)
            return {
                "content": f"웹 스크래핑 실패: {str(e)}",
                "title": "",
                "url": url,
                "char_count": 0,
            }
