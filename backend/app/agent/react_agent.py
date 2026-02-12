"""
Main ReAct Agent loop using LangChain/LangGraph.

Flow: Intent Classification -> Tool Execution -> LLM Inference -> Evaluation -> Re-query
Yields SSE events at each step for real-time UI updates.
"""
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.intent_classifier import IntentClassifier
from app.agent.tool_executor import ToolExecutor
from app.agent.evaluator import Evaluator
from app.agent.token_tracker import TokenTracker
from app.config import settings
from app.db.models import Agent, AgentTool, ChatMessage, User

logger = logging.getLogger(__name__)


class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent that orchestrates:
    1. Intent classification
    2. Tool selection & execution
    3. LLM inference with context
    4. Answer evaluation
    5. Re-query if quality insufficient
    """

    def __init__(self, db: AsyncSession, agent: Agent, user: User):
        self.db = db
        self.agent = agent
        self.user = user
        self.intent_classifier = IntentClassifier()
        self.tool_executor = ToolExecutor(db, agent, user)
        self.evaluator = Evaluator()
        self.token_tracker = TokenTracker(db, user, agent)
        self.max_iterations = settings.react_max_iterations
        self.eval_threshold = settings.react_evaluation_threshold

    async def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """Run the agent synchronously and return final result."""
        result = {
            "response": "",
            "tool_calls": [],
            "token_usage": {},
            "latency_ms": 0,
        }
        start = time.time()

        async for event_type, event_data in self.run_stream(query, **kwargs):
            if event_type == "answer_token":
                result["response"] += event_data.get("token", "")
            elif event_type in ("tool_start", "tool_result"):
                result["tool_calls"].append(event_data)
            elif event_type == "answer_end":
                result["token_usage"] = event_data.get("usage", {})

        result["latency_ms"] = int((time.time() - start) * 1000)
        return result

    async def run_stream(
        self,
        query: str,
        history: Optional[List[ChatMessage]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Tuple[str, Dict[str, Any]], None]:
        """
        Run the ReAct loop, yielding SSE events at each step.

        Events:
        - thinking: intent classification result
        - tool_start: tool about to execute
        - tool_result: tool execution result
        - evaluation: answer quality evaluation
        - answer_token: streaming token from LLM
        - answer_end: final usage statistics
        """
        iteration = 0
        tool_results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        while iteration < self.max_iterations:
            iteration += 1

            # Step 1: Intent Classification
            intent = await self.intent_classifier.classify(query, tool_results)
            yield "thinking", {
                "intent": intent.intent_type,
                "confidence": intent.confidence,
                "reasoning": intent.reasoning,
                "iteration": iteration,
            }

            # Step 2: Tool Execution (if needed)
            if intent.intent_type != "general_chat":
                tools = await self.tool_executor.get_enabled_tools()
                for tool in tools:
                    if self._should_use_tool(intent.intent_type, tool):
                        tool_start_time = time.time()

                        yield "tool_start", {
                            "tool": tool.tool_type,
                            "input": {"query": query},
                            "iteration": iteration,
                        }

                        tool_output = await self.tool_executor.execute(
                            tool, query, context=tool_results
                        )
                        duration_ms = int((time.time() - tool_start_time) * 1000)

                        tool_results.append(tool_output)

                        yield "tool_result", {
                            "tool": tool.tool_type,
                            "output": tool_output,
                            "duration_ms": duration_ms,
                            "iteration": iteration,
                        }

            # Step 3: LLM Inference with streaming
            messages = self._build_messages(query, history, tool_results)
            full_response = ""

            async for token, usage in self._stream_llm(messages, config):
                if token:
                    full_response += token
                    yield "answer_token", {"token": token}
                if usage:
                    for key in total_usage:
                        total_usage[key] += usage.get(key, 0)

            # Step 4: Evaluation
            score = await self.evaluator.evaluate(query, full_response, tool_results)
            passed = score >= self.eval_threshold

            yield "evaluation", {
                "score": score,
                "threshold": self.eval_threshold,
                "pass": passed,
                "iteration": iteration,
            }

            # If evaluation passes or max iterations reached, finalize
            if passed or iteration >= self.max_iterations:
                # Track usage
                await self.token_tracker.track(total_usage)

                yield "answer_end", {
                    "usage": total_usage,
                    "iterations": iteration,
                    "final_score": score,
                }
                break

            # Step 5: Re-query - modify query for next iteration
            query = f"Please provide a more detailed answer. Original question: {query}"

    def _should_use_tool(self, intent_type: str, tool: AgentTool) -> bool:
        """Determine if a tool should be used based on intent."""
        mapping = {
            "rag_search": ["rag"],
            "web_search": ["web_search"],
            "hybrid": ["rag", "web_search"],
        }
        allowed = mapping.get(intent_type, [])
        return tool.tool_type in allowed

    def _build_messages(
        self,
        query: str,
        history: Optional[List[ChatMessage]],
        tool_results: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """Build LLM message list with system prompt, history, tool context, and query."""
        messages = []

        # System prompt
        if self.agent.system_prompt:
            messages.append({"role": "system", "content": self.agent.system_prompt})

        # History
        if history:
            for msg in history[-10:]:  # Last 10 messages
                messages.append({"role": msg.role, "content": msg.content})

        # Tool context
        if tool_results:
            context_parts = []
            for result in tool_results:
                tool_type = result.get("tool_type", "unknown")
                output = result.get("output", "")
                context_parts.append(f"[{tool_type} result]: {output}")
            context = "\n\n".join(context_parts)
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer the user's question:\n\n{context}",
            })

        # User query
        messages.append({"role": "user", "content": query})

        return messages

    async def _stream_llm(
        self,
        messages: List[Dict[str, str]],
        config: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Tuple[Optional[str], Optional[Dict]], None]:
        """Stream tokens from the LLM via Open Router."""
        model_id = "openai/gpt-4o"
        if self.agent.model_id:
            from sqlalchemy import select
            from app.db.models import Model

            result = await self.db.execute(
                select(Model).where(Model.id == self.agent.model_id, Model.use_yn == "Y")
            )
            model = result.scalar_one_or_none()
            if model:
                model_id = model.model_id

        request_body = {
            "model": model_id,
            "messages": messages,
            "stream": True,
        }

        if config:
            if "temperature" in config:
                request_body["temperature"] = config["temperature"]
            if "max_tokens" in config:
                request_body["max_tokens"] = config["max_tokens"]

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_body,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                import json
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content, None

                                usage = data.get("usage")
                                if usage:
                                    yield None, usage
                            except Exception:
                                continue
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            yield f"Error communicating with LLM: {str(e)}", None
