"""
Answer quality evaluator.

Evaluates the quality of generated answers on a 0-1 scale.
If score < threshold (0.7), the ReAct loop will re-query.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluate answer quality to determine if re-query is needed."""

    async def evaluate(
        self,
        query: str,
        answer: str,
        tool_results: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """
        Evaluate the quality of an answer.

        Scoring criteria:
        - Length: Very short answers score lower
        - Relevance: Answer should contain keywords from query
        - Tool usage: If tools were used, answer should reference their results
        - Error detection: Answers containing error messages score lower

        Args:
            query: Original user query
            answer: Generated answer
            tool_results: Results from tool executions

        Returns:
            Score between 0.0 and 1.0
        """
        if not answer or not answer.strip():
            return 0.0

        score = 0.5  # Base score

        # Length scoring
        word_count = len(answer.split())
        if word_count < 5:
            score -= 0.2
        elif word_count > 20:
            score += 0.1
        elif word_count > 50:
            score += 0.15

        # Error detection
        error_indicators = ["error", "failed", "unable to", "cannot", "sorry"]
        answer_lower = answer.lower()
        error_count = sum(1 for ei in error_indicators if ei in answer_lower)
        score -= error_count * 0.1

        # Relevance scoring - check if query keywords appear in answer
        query_words = set(query.lower().split())
        # Remove common words
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "what", "how", "why",
                      "when", "where", "who", "do", "does", "did", "to", "in", "of", "and",
                      "or", "for", "with", "on", "at", "by", "about"}
        query_keywords = query_words - stopwords
        if query_keywords:
            overlap = sum(1 for kw in query_keywords if kw in answer_lower)
            relevance_ratio = overlap / len(query_keywords)
            score += relevance_ratio * 0.2

        # Tool result integration
        if tool_results:
            successful_tools = [r for r in tool_results if r.get("success")]
            if successful_tools and word_count > 10:
                score += 0.1

        # Clamp score to [0, 1]
        return max(0.0, min(1.0, score))
