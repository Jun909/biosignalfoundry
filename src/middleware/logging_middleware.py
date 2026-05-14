import time
from typing import Any, Awaitable, Callable

import structlog
from langchain.agents.middleware import (AgentMiddleware, AgentState,
                                         ModelRequest, ModelResponse)
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

logger = structlog.get_logger()


class LoggingMiddleware(AgentMiddleware):
    """
    Reusable logging middleware for LangChain agents.

    Logs:
      - before_agent:  the input the agent receives (from supervisor or user)
      - after_model:   the model's decision (tool calls it wants to make, or final answer)
      - wrap_tool_call: each tool execution with timing
      - after_agent:   the final response the agent passes back

    Usage:
        agent = create_agent(
            model=llm,
            tools=[...],
            middleware=[LoggingMiddleware(agent_name="financial_health")],
        )
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    # -- async hooks (used by ainvoke) --

    async def abefore_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        logger.info(
            "agent started",
            agent=self.agent_name,
            input_message=getattr(last_msg, "content", None),
            message_count=len(messages),
        )
        return None

    async def aafter_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None

        tool_calls = getattr(last_msg, "tool_calls", None)
        if tool_calls:
            tool_names = [tc["name"] for tc in tool_calls]
            logger.info(
                "model requested tool calls",
                agent=self.agent_name,
                tools=tool_names,
            )
        else:
            content = getattr(last_msg, "content", "")
            preview = content[:200] if isinstance(content, str) else str(content)[:200]
            logger.info(
                "model returned final answer",
                agent=self.agent_name,
                response_preview=preview,
            )
        return None

    async def aafter_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        content = getattr(last_msg, "content", "")
        preview = content[:200] if isinstance(content, str) else str(content)[:200]
        logger.info(
            "agent completed",
            agent=self.agent_name,
            response_preview=preview,
        )
        return None

    # -- sync hooks (used by invoke) --

    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        logger.info(
            "agent started",
            agent=self.agent_name,
            input_message=getattr(last_msg, "content", None),
            message_count=len(messages),
        )
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None

        tool_calls = getattr(last_msg, "tool_calls", None)
        if tool_calls:
            tool_names = [tc["name"] for tc in tool_calls]
            logger.info(
                "model requested tool calls",
                agent=self.agent_name,
                tools=tool_names,
            )
        else:
            content = getattr(last_msg, "content", "")
            preview = content[:200] if isinstance(content, str) else str(content)[:200]
            logger.info(
                "model returned final answer",
                agent=self.agent_name,
                response_preview=preview,
            )
        return None

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        content = getattr(last_msg, "content", "")
        preview = content[:200] if isinstance(content, str) else str(content)[:200]
        logger.info(
            "agent completed",
            agent=self.agent_name,
            response_preview=preview,
        )
        return None

    # -- wrap-style hook for tool calls --

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call["args"]

        logger.info(
            "tool call started",
            agent=self.agent_name,
            tool=tool_name,
            tool_args=tool_args,
        )
        start = time.perf_counter()
        try:
            result = await handler(request)
            duration_ms = round((time.perf_counter() - start) * 1000)
            logger.info(
                "tool call completed",
                agent=self.agent_name,
                tool=tool_name,
                duration_ms=duration_ms,
            )
            return result
        except Exception as e:
            duration_ms = round((time.perf_counter() - start) * 1000)
            logger.error(
                "tool call failed",
                agent=self.agent_name,
                tool=tool_name,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call["args"]

        logger.info(
            "tool call started",
            agent=self.agent_name,
            tool=tool_name,
            tool_args=tool_args,
        )
        start = time.perf_counter()
        try:
            result = handler(request)
            duration_ms = round((time.perf_counter() - start) * 1000)
            logger.info(
                "tool call completed",
                agent=self.agent_name,
                tool=tool_name,
                duration_ms=duration_ms,
            )
            return result
        except Exception as e:
            duration_ms = round((time.perf_counter() - start) * 1000)
            logger.error(
                "tool call failed",
                agent=self.agent_name,
                tool=tool_name,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
