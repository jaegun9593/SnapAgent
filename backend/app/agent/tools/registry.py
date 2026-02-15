"""
Tool registry for central tool management and factory pattern.

All tool classes (except RAG, which requires DB context) are registered here
for lookup by tool_type string.
"""
from typing import Dict, List, Optional, Type

from app.agent.tools.base import BaseTool

TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {}


def get_tool_class(tool_type: str) -> Optional[Type[BaseTool]]:
    """Look up a tool class by its type string."""
    return TOOL_REGISTRY.get(tool_type)


# Category definitions
TOOL_CATEGORIES: Dict[str, List[str]] = {
    "web_search": ["web_search", "tavily_search"],
    "document": ["rag"],
    "academic": ["wikipedia", "arxiv"],
    "code": ["calculator", "python_repl"],
    "data": ["web_scraper", "custom_api"],
}

# Purpose → recommended tools mapping
PURPOSE_RECOMMENDATIONS: Dict[str, List[str]] = {
    "research": ["web_search", "tavily_search", "wikipedia", "web_scraper"],
    "qa": ["rag"],
    "summary": ["rag", "web_scraper"],
    "monitoring": ["web_search", "tavily_search", "web_scraper"],
}

# Tool type → intent type mapping (for IntentClassifier)
TOOL_INTENT_MAP: Dict[str, str] = {
    "rag": "rag_search",
    "web_search": "web_search",
    "tavily_search": "web_search",
    "wikipedia": "web_search",
    "arxiv": "web_search",
    "calculator": "general_chat",
    "python_repl": "general_chat",
    "web_scraper": "web_search",
    "custom_api": "general_chat",
}


def _auto_register() -> None:
    """Import and register all tool classes."""
    from app.agent.tools.web_search_tool import WebSearchTool
    from app.agent.tools.tavily_tool import TavilySearchTool
    from app.agent.tools.wikipedia_tool import WikipediaTool
    from app.agent.tools.arxiv_tool import ArxivTool
    from app.agent.tools.calculator_tool import CalculatorTool
    from app.agent.tools.python_repl_tool import PythonReplTool
    from app.agent.tools.web_scraper_tool import WebScraperTool
    from app.agent.tools.custom_api_tool import CustomApiTool

    TOOL_REGISTRY["web_search"] = WebSearchTool
    TOOL_REGISTRY["tavily_search"] = TavilySearchTool
    TOOL_REGISTRY["wikipedia"] = WikipediaTool
    TOOL_REGISTRY["arxiv"] = ArxivTool
    TOOL_REGISTRY["calculator"] = CalculatorTool
    TOOL_REGISTRY["python_repl"] = PythonReplTool
    TOOL_REGISTRY["web_scraper"] = WebScraperTool
    TOOL_REGISTRY["custom_api"] = CustomApiTool
    # RAG tool requires (db, agent, user) — handled specially in ToolExecutor


_auto_register()
