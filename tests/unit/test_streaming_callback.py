"""
Tests for src/core/streaming_callback.py — StreamingProgressCallback.

The callback is the bridge between LangChain tool execution events and the
SSE stream sent to the client.  Its job is simple: translate a tool name
into a human-readable label and push a 'progress' event onto the queue.

These tests are pure asyncio — no mocking of external services needed.
"""

import asyncio

from src.core.streaming_callback import TOOL_LABELS, StreamingProgressCallback


# ---------------------------------------------------------------------------
# Test 1 — known tool name is translated to the configured label
# ---------------------------------------------------------------------------

async def test_known_tool_name_emits_mapped_label():
    """
    Tools registered in TOOL_LABELS must emit their human-readable label,
    not the raw internal name.

    Why: the client shows these messages in the UI progress indicator.
    Raw names like 'get_income_statement_annual' are confusing for users.
    """
    queue: asyncio.Queue = asyncio.Queue()
    cb = StreamingProgressCallback(queue)

    await cb.on_tool_start({"name": "get_company_profile"}, "NVDA")

    event = queue.get_nowait()
    assert event["type"] == "progress"
    assert event["message"] == TOOL_LABELS["get_company_profile"]
    assert event["message"] == "Fetching company profile"


async def test_all_registered_tools_emit_their_configured_labels():
    """
    Every entry in TOOL_LABELS must produce exactly its configured label.

    This acts as a contract test: if someone renames a tool or changes a
    label, this test surfaces the mismatch immediately.
    """
    for tool_name, expected_label in TOOL_LABELS.items():
        queue: asyncio.Queue = asyncio.Queue()
        cb = StreamingProgressCallback(queue)

        await cb.on_tool_start({"name": tool_name}, "some_input")

        event = queue.get_nowait()
        assert event["type"] == "progress", f"Wrong event type for tool '{tool_name}'"
        assert event["message"] == expected_label, (
            f"Tool '{tool_name}': expected label '{expected_label}', "
            f"got '{event['message']}'"
        )


# ---------------------------------------------------------------------------
# Test 2 — unknown tool name falls back gracefully
# ---------------------------------------------------------------------------

async def test_unknown_tool_name_emits_fallback_label():
    """
    A tool not listed in TOOL_LABELS must not raise — it must emit a
    generic 'Running <name>...' fallback so new tools produce a visible
    progress event without requiring a label to be registered first.
    """
    queue: asyncio.Queue = asyncio.Queue()
    cb = StreamingProgressCallback(queue)

    await cb.on_tool_start({"name": "some_future_tool"}, "any_input")

    event = queue.get_nowait()
    assert event["type"] == "progress"
    assert "some_future_tool" in event["message"]


# ---------------------------------------------------------------------------
# Test 3 — missing 'name' key in serialized dict falls back safely
# ---------------------------------------------------------------------------

async def test_missing_name_key_emits_fallback_label():
    """
    LangChain may call on_tool_start with a serialized dict that lacks the
    'name' key (e.g. for anonymous tools).  The callback must not raise —
    it falls back to TOOL_LABELS.get("", f"Running ...") which produces
    the generic fallback because "" is not a registered tool name.
    """
    queue: asyncio.Queue = asyncio.Queue()
    cb = StreamingProgressCallback(queue)

    await cb.on_tool_start({}, "some_input")   # no 'name' key

    event = queue.get_nowait()
    assert event["type"] == "progress"
    # Must not raise; exact message is an implementation detail


# ---------------------------------------------------------------------------
# Test 4 — each call pushes exactly one event onto the queue
# ---------------------------------------------------------------------------

async def test_on_tool_start_pushes_exactly_one_event():
    """
    Each on_tool_start invocation must enqueue exactly one event.
    If it pushed zero (silent), the UI would show no progress.
    If it pushed multiple, the UI would stutter.
    """
    queue: asyncio.Queue = asyncio.Queue()
    cb = StreamingProgressCallback(queue)

    await cb.on_tool_start({"name": "get_income_statement_annual"}, "NVDA")

    assert queue.qsize() == 1
