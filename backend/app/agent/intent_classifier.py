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

    # Keywords that suggest academic/research intent
    ACADEMIC_KEYWORDS = [
        "논문", "연구", "학술", "arxiv", "paper", "research",
        "journal", "학회", "학자", "인용",
    ]

    # Keywords that suggest code/calculation intent
    CODE_KEYWORDS = [
        "코드", "프로그래밍", "계산", "수식", "파이썬", "python",
        "calculate", "compute", "code", "실행", "연산",
    ]

    # Keywords that suggest web scraping intent
    SCRAPER_KEYWORDS = [
        "페이지", "사이트", "URL", "링크", "스크래핑",
        "추출", "scrape", "crawl", "크롤링",
    ]

    # Preference-based score weights for task_purpose
    PURPOSE_WEIGHTS: Dict[str, Dict[str, int]] = {
        "research": {"web_search": 2},
        "monitoring": {"web_search": 2},
        "qa": {"rag": 2},
        "summary": {"rag": 2},
    }

    async def classify(
        self,
        query: str,
        previous_results: Optional[List[Dict[str, Any]]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> IntentResult:
        """
        Classify the user's intent from their query.

        Args:
            query: The user's question
            previous_results: Results from previous tool executions (for re-query)
            preferences: Agent preferences dict with task_purpose, response_format, response_tone

        Returns:
            IntentResult with classified intent
        """
        query_lower = query.lower()

        rag_score = sum(1 for kw in self.RAG_KEYWORDS if kw in query_lower)
        web_score = sum(1 for kw in self.WEB_KEYWORDS if kw in query_lower)

        # Academic keywords boost web_search (arxiv, wikipedia are web_search intent)
        academic_score = sum(1 for kw in self.ACADEMIC_KEYWORDS if kw in query_lower)
        web_score += academic_score

        # Scraper keywords also boost web_search intent
        scraper_score = sum(1 for kw in self.SCRAPER_KEYWORDS if kw in query_lower)
        web_score += scraper_score

        # Code/calculation keywords: these tools run under general_chat,
        # but we still want to trigger tool execution, so give a small web boost
        # to avoid falling into pure general_chat (which skips tools)
        code_score = sum(1 for kw in self.CODE_KEYWORDS if kw in query_lower)

        # Apply preference-based weights
        if preferences:
            task_purpose = preferences.get("task_purpose", "")
            weights = self.PURPOSE_WEIGHTS.get(task_purpose, {})
            rag_score += weights.get("rag", 0)
            web_score += weights.get("web_search", 0)

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
        elif code_score > 0:
            # Code/calculation queries: use general_chat intent but tools will
            # still fire because _should_use_tool handles code tools specially
            return IntentResult(
                intent_type="general_chat",
                confidence=0.7,
                reasoning=f"Query contains {code_score} code/calculation indicators",
            )
        else:
            return IntentResult(
                intent_type="general_chat",
                confidence=0.8,
                reasoning="No specific tool indicators found, treating as general conversation",
            )
