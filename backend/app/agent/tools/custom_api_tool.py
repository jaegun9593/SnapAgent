"""
Custom API call tool for integrating external APIs.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


class CustomApiTool(BaseTool):
    """Tool for making custom API calls."""

    @property
    def name(self) -> str:
        return "custom_api"

    @property
    def description(self) -> str:
        return "Make custom API calls to external services"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute custom API call."""
        return await self.call(query, config=config)

    async def call(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a custom API call.

        Args:
            query: The query or data to send
            config: Configuration with url, method, headers, body_template

        Returns:
            Dict with content string and response data
        """
        if not config:
            return {"content": "No API configuration provided", "response": {}}

        url = config.get("url")
        method = config.get("method", "POST").upper()
        headers = config.get("headers", {})
        body_template = config.get("body_template", {})
        timeout = config.get("timeout", 30)

        if not url:
            return {"content": "No API URL configured", "response": {}}

        try:
            # Inject query into body template
            body = {**body_template}
            if "query" in body:
                body["query"] = query
            elif not body:
                body = {"query": query}

            async with httpx.AsyncClient(timeout=float(timeout)) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=body)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=body)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=body)
                else:
                    return {"content": f"Unsupported method: {method}", "response": {}}

                response.raise_for_status()
                response_data = response.json()

            # Extract content from response
            content_field = config.get("content_field", None)
            if content_field and content_field in response_data:
                content = str(response_data[content_field])
            else:
                content = str(response_data)

            return {
                "content": content,
                "response": {
                    "status_code": response.status_code,
                    "data": response_data,
                },
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Custom API HTTP error: {e}")
            return {
                "content": f"API call failed with status {e.response.status_code}",
                "response": {"error": str(e)},
            }
        except Exception as e:
            logger.error(f"Custom API error: {e}")
            return {
                "content": f"API call failed: {str(e)}",
                "response": {"error": str(e)},
            }
