"""
Safe math calculator tool using numexpr.
"""
import logging
import re
from typing import Any, Dict, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)

# Allowed characters in math expressions
_SAFE_PATTERN = re.compile(r"^[\d\s\+\-\*/\(\)\.\,\^%eE]+$")


class CalculatorTool(BaseTool):
    """Safe math expression calculator using numexpr."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Calculate mathematical expressions safely"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a math expression.

        Args:
            query: Math expression string (e.g., "2 * 3 + 5")
            config: Not used

        Returns:
            Dict with content (result string) and result (numeric value)
        """
        expression = query.strip()

        # Replace common math notation
        expression = expression.replace("^", "**")
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")

        # Basic safety check — block import, exec, eval, etc.
        dangerous = ["import", "exec", "eval", "__", "open", "os.", "sys."]
        for token in dangerous:
            if token in expression.lower():
                return {
                    "content": f"안전하지 않은 수식입니다: '{token}' 사용 불가",
                    "result": None,
                }

        try:
            import numexpr

            result = numexpr.evaluate(expression)
            result_value = float(result)
            return {
                "content": f"{query.strip()} = {result_value}",
                "result": result_value,
            }
        except Exception as e:
            logger.error("Calculator error: %s", e)
            return {
                "content": f"계산 실패: {str(e)}",
                "result": None,
            }
