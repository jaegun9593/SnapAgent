"""
Sandboxed Python code execution tool using RestrictedPython.
"""
import io
import logging
import signal
from typing import Any, Dict, Optional

from app.agent.tools.base import BaseTool

logger = logging.getLogger(__name__)


def _timeout_handler(signum: int, frame: Any) -> None:
    raise TimeoutError("Python code execution timed out")


class PythonReplTool(BaseTool):
    """Sandboxed Python code execution tool."""

    @property
    def name(self) -> str:
        return "python_repl"

    @property
    def description(self) -> str:
        return "Execute Python code in a restricted sandbox"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code in a RestrictedPython sandbox.

        Args:
            query: Python code string
            config: Configuration with timeout (seconds)

        Returns:
            Dict with content (stdout output) and success flag
        """
        config = config or {}
        timeout = config.get("timeout", 10)
        code = query.strip()

        if not code:
            return {"content": "실행할 코드가 없습니다.", "success": False}

        try:
            from RestrictedPython import compile_restricted, safe_globals
            from RestrictedPython.Eval import default_guarded_getiter
            from RestrictedPython.Guards import (
                guarded_unpack_sequence,
                safer_getattr,
            )

            # Compile with RestrictedPython
            compiled = compile_restricted(code, "<agent>", "exec")
            if compiled.errors:
                return {
                    "content": f"코드 컴파일 오류: {'; '.join(compiled.errors)}",
                    "success": False,
                }

            # Set up restricted globals with stdout capture
            stdout_capture = io.StringIO()
            restricted_globals = safe_globals.copy()
            restricted_globals["_print_"] = lambda: stdout_capture.write
            restricted_globals["_getiter_"] = default_guarded_getiter
            restricted_globals["_getattr_"] = safer_getattr
            restricted_globals["_unpack_sequence_"] = guarded_unpack_sequence
            restricted_globals["_write_"] = lambda obj: obj

            # Allow basic built-ins
            restricted_globals["__builtins__"]["__import__"] = None  # Block imports
            for name in ["range", "len", "str", "int", "float", "bool", "list",
                         "dict", "tuple", "set", "sorted", "enumerate", "zip",
                         "map", "filter", "sum", "min", "max", "abs", "round",
                         "print", "type", "isinstance"]:
                restricted_globals["__builtins__"][name] = __builtins__[name] if isinstance(__builtins__, dict) else getattr(__builtins__, name)

            restricted_locals: Dict[str, Any] = {}

            # Execute with timeout (Unix only)
            old_handler = None
            try:
                old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(timeout)
                exec(compiled.code, restricted_globals, restricted_locals)
                signal.alarm(0)
            except TimeoutError:
                return {
                    "content": f"코드 실행 시간 초과 ({timeout}초)",
                    "success": False,
                }
            finally:
                signal.alarm(0)
                if old_handler is not None:
                    signal.signal(signal.SIGALRM, old_handler)

            output = stdout_capture.getvalue()
            if not output and "_result" in restricted_locals:
                output = str(restricted_locals["_result"])

            return {
                "content": output if output else "(코드 실행 완료, 출력 없음)",
                "success": True,
            }

        except ImportError:
            logger.warning("RestrictedPython not installed, falling back to disabled")
            return {
                "content": "Python 실행 기능이 비활성화되어 있습니다. (RestrictedPython 미설치)",
                "success": False,
            }
        except Exception as e:
            logger.error("Python REPL error: %s", e)
            return {
                "content": f"코드 실행 오류: {str(e)}",
                "success": False,
            }
