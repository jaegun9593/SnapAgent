"""
Intent classifier for determining the user's intent.

Classifies queries into:
- rag_search: User wants to search uploaded documents
- web_search: User wants to search the web
- general_chat: General conversation, no tool needed
- hybrid: Both RAG and web search needed
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent classification."""

    intent_type: str  # 'rag_search', 'web_search', 'general_chat', 'hybrid'
    confidence: float  # 0.0 - 1.0
    reasoning: str  # Why this intent was chosen


class IntentClassifier:
    """Classify user intent to determine which tools to use."""

    # Keywords that suggest RAG search
    RAG_KEYWORDS = [
        "문서", "파일", "업로드", "자료", "내용", "찾아", "검색",
        "document", "file", "uploaded", "content", "search", "find",
        "according to", "based on", "in the",
    ]

    # Keywords that suggest web search
    WEB_KEYWORDS = [
        "최신", "뉴스", "현재", "오늘", "날씨", "실시간",
        "latest", "news", "current", "today", "weather", "real-time",
        "what is", "who is", "how to",
    ]

    async def classify(
        self, query: str, previous_results: Optional[List[Dict[str, Any]]] = None
    ) -> IntentResult:
        """
        Classify the user's intent from their query.

        Args:
            query: The user's question
            previous_results: Results from previous tool executions (for re-query)

        Returns:
            IntentResult with classified intent
        """
        query_lower = query.lower()

        rag_score = sum(1 for kw in self.RAG_KEYWORDS if kw in query_lower)
        web_score = sum(1 for kw in self.WEB_KEYWORDS if kw in query_lower)

        # If this is a re-query iteration with previous results, prefer different tools
        if previous_results:
            previous_tools = [r.get("tool_type") for r in previous_results]
            if "rag" in previous_tools and "web_search" not in previous_tools:
                web_score += 2
            elif "web_search" in previous_tools and "rag" not in previous_tools:
                rag_score += 2

        # Determine intent
        if rag_score > 0 and web_score > 0:
            return IntentResult(
                intent_type="hybrid",
                confidence=0.7,
                reasoning=f"Query contains both document ({rag_score}) and web ({web_score}) search indicators",
            )
        elif rag_score > web_score:
            return IntentResult(
                intent_type="rag_search",
                confidence=min(0.5 + rag_score * 0.1, 0.95),
                reasoning=f"Query contains {rag_score} document search indicators",
            )
        elif web_score > rag_score:
            return IntentResult(
                intent_type="web_search",
                confidence=min(0.5 + web_score * 0.1, 0.95),
                reasoning=f"Query contains {web_score} web search indicators",
            )
        else:
            return IntentResult(
                intent_type="general_chat",
                confidence=0.8,
                reasoning="No specific tool indicators found, treating as general conversation",
            )
