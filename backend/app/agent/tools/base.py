"""
Base tool abstract class for agent tools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Abstract base class for all agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for intent classification."""
        ...

    @abstractmethod
    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the tool with the given query.

        Args:
            query: The search query or input
            config: Tool-specific configuration

        Returns:
            Dict containing 'content' (str) and tool-specific metadata
        """
        ...
