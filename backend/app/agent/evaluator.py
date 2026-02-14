"""
Answer quality evaluator.

Evaluates the quality of generated answers on a 0-1 scale.
If score < threshold (0.7), the ReAct loop will re-query.

Korean-aware: uses character length instead of word count since Korean
has fewer whitespace-delimited tokens than English.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluate answer quality to determine if re-query is needed."""

    # Korean + English stopwords (excluded from relevance scoring)
    STOPWORDS = {
        # English
        "the", "a", "an", "is", "are", "was", "were", "what", "how", "why",
        "when", "where", "who", "do", "does", "did", "to", "in", "of", "and",
        "or", "for", "with", "on", "at", "by", "about",
        # Korean
        "은", "는", "이", "가", "을", "를", "의", "에", "에서", "도", "로",
        "으로", "와", "과", "하고", "이다", "입니다", "해줘", "알려줘", "뭐야",
    }

    async def evaluate(
        self,
        query: str,
        answer: str,
        tool_results: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """
        Evaluate the quality of an answer.

        Scoring criteria:
        - Length: character-based (Korean-friendly)
        - Relevance: Answer should contain keywords from query
        - Tool usage: If tools were used, answer should reference their results
        - Error detection: Answers containing error messages score lower

        Returns:
            Score between 0.0 and 1.0
        """
        if not answer or not answer.strip():
            return 0.0

        score = 0.6  # Base score
        answer_lower = answer.lower()
        char_count = len(answer.strip())

        # Length scoring (character-based for Korean support)
        if char_count < 2:
            score -= 0.2
        elif char_count >= 10:
            score += 0.15
        elif char_count >= 50:
            score += 0.2

        # Error detection
        error_indicators = ["error", "failed", "unable to", "cannot", "오류", "실패", "불가"]
        error_count = sum(1 for ei in error_indicators if ei in answer_lower)
        score -= error_count * 0.1

        # Relevance scoring - check if query keywords appear in answer
        query_words = set(query.lower().split())
        query_keywords = query_words - self.STOPWORDS
        if query_keywords:
            overlap = sum(1 for kw in query_keywords if kw in answer_lower)
            relevance_ratio = overlap / len(query_keywords)
            score += relevance_ratio * 0.2

        # Tool result integration
        if tool_results:
            successful_tools = [r for r in tool_results if r.get("success")]
            if successful_tools and char_count > 20:
                score += 0.1

        # Clamp score to [0, 1]
        return max(0.0, min(1.0, score))
