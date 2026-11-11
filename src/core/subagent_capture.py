"""
Capture each subagent's own structured response during a supervisor run.

deepagents drops a subagent's ``structured_response`` from the state it returns and
hands the supervisor only the text ``Returning structured response: <repr>``. To
store the typed output (so fields like ``score`` stay queryable) the subagent's
runnable is wrapped: it records ``structured_response`` into a collector held in a
context variable, then returns the subagent's result unchanged, so the supervisor
sees exactly what it saw before. Outside ``capture_subagent_outputs()`` the wrapper
does nothing.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from langchain_core.runnables import Runnable, RunnableLambda

_collector: ContextVar[list[dict] | None] = ContextVar("subagent_outputs", default=None)


@contextmanager
def capture_subagent_outputs() -> Iterator[list[dict]]:
    """Collect ``{"subagent", "task", "output"}`` for every subagent run inside."""
    outputs: list[dict] = []
    token = _collector.set(outputs)
    try:
        yield outputs
    finally:
        _collector.reset(token)


def _task_text(state: Any) -> str | None:
    messages = state.get("messages") if isinstance(state, dict) else None
    if not messages:
        return None
    content = getattr(messages[0], "content", None)
    return content if isinstance(content, str) else None


def _record(name: str, state: Any, result: Any) -> None:
    outputs = _collector.get()
    if outputs is None or not isinstance(result, dict):
        return
    response = result.get("structured_response")
    if response is None:
        return
    outputs.append(
        {
            "subagent": name,
            "task": _task_text(state),
            "output": (
                response.model_dump(mode="json")
                if hasattr(response, "model_dump")
                else response
            ),
        }
    )


def capture_structured_output(name: str, runnable: Runnable) -> Runnable:
    """Wrap a subagent runnable so its structured response is captured (see module doc)."""

    def invoke(state, config=None):
        result = runnable.invoke(state, config)
        _record(name, state, result)
        return result

    async def ainvoke(state, config=None):
        result = await runnable.ainvoke(state, config)
        _record(name, state, result)
        return result

    return RunnableLambda(invoke, afunc=ainvoke, name=name)
