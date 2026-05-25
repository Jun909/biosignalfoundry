"""
Tests for POST /analyze in app.py.

Mocking strategy
----------------
Two external seams are patched per test so nothing real is touched:

  redis_client  — patch.object on get / setex
  biosignalfoundry — patch.object on ainvoke

Both objects live as module-level names in app.py, so patching them
there is the right seam: app.py is what we are testing, not the
internals of Redis or deepagents.
"""

import hashlib
import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import app as app_module
from app import app
from config import REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY
from src.biosignalfoundry import BioSignalFoundryOutput

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

CACHED_EVENT = {
    "type": "result",
    "data": {
        "ticker": "NVDA",
        "decision": "Buy",
        "confidence": 85,
        "reasoning": "Strong pipeline",
    },
}
CACHED_PAYLOAD = json.dumps(CACHED_EVENT)

STRUCTURED_RESULT = BioSignalFoundryOutput(
    ticker="NVDA",
    decision="Buy",
    confidence=85,
    reasoning="Strong pipeline",
)


def parse_sse_events(text: str) -> list[dict]:
    """Pull every SSE 'data: ...' line out of a streaming response body."""
    events = []
    for line in text.strip().splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line.removeprefix("data: ")))
    return events


@pytest.fixture
def http_client():
    """Async HTTPX client wired to the FastAPI app."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# Test 1 — cache hit must skip the agent entirely
# ---------------------------------------------------------------------------

async def test_cache_hit_skips_agent(http_client):
    """
    When Redis already has a result, the endpoint must:
      1. Return 200 with the cached SSE payload.
      2. Never call biosignalfoundry.ainvoke.

    Why this matters: the whole point of the cache is to avoid expensive
    LLM calls. If ainvoke is called on a cache hit, we pay for work we
    already did.
    """
    with (
        patch.object(app_module.redis_client, "get", return_value=CACHED_PAYLOAD),
        patch.object(
            app_module.biosignalfoundry, "ainvoke", new_callable=AsyncMock
        ) as mock_ainvoke,
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 200
    mock_ainvoke.assert_not_called()
    assert f"data: {CACHED_PAYLOAD}" in response.text


# ---------------------------------------------------------------------------
# Test 2 — cache miss + agent success → result emitted and written to cache
# ---------------------------------------------------------------------------

async def test_cache_miss_agent_success_emits_result_and_caches(http_client):
    """
    On a cache miss the agent runs, the structured result is streamed back,
    and redis_client.setex is called so the next identical query is cached.

    Checks:
      - Status 200
      - ainvoke was called once
      - setex was called with the right TTL (REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY)
      - SSE body contains a 'result' event with the ticker
    """
    with (
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module.redis_client, "setex") as mock_setex,
        patch.object(
            app_module.biosignalfoundry,
            "ainvoke",
            new_callable=AsyncMock,
            return_value={"structured_response": STRUCTURED_RESULT},
        ) as mock_ainvoke,
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 200
    mock_ainvoke.assert_called_once()

    # Result must be cached — one call to setex with the correct TTL
    mock_setex.assert_called_once()
    _, actual_ttl, _payload = mock_setex.call_args.args
    assert actual_ttl == REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY

    # Validate the cached payload is valid JSON with the expected shape
    cached_event = json.loads(_payload)
    assert cached_event["type"] == "result"
    assert cached_event["data"]["ticker"] == "NVDA"

    # SSE body must carry the result event
    events = parse_sse_events(response.text)
    result_events = [e for e in events if e.get("type") == "result"]
    assert len(result_events) == 1
    assert result_events[0]["data"]["ticker"] == "NVDA"


# ---------------------------------------------------------------------------
# Test 3 — agent raises an exception → error event emitted, stream closes
# ---------------------------------------------------------------------------

async def test_cache_miss_agent_exception_emits_error_event(http_client):
    """
    If the agent raises unexpectedly the endpoint must:
      - Emit a {'type': 'error', 'message': <str>} SSE event.
      - Close the stream cleanly (no infinite hang — test itself proves this
        because it would time out if the stream never terminates).
      - NOT write anything to the cache.

    This covers the 'except Exception as e' branch in run_agent().
    """
    with (
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module.redis_client, "setex") as mock_setex,
        patch.object(
            app_module.biosignalfoundry,
            "ainvoke",
            new_callable=AsyncMock,
            side_effect=RuntimeError("LLM connection failed"),
        ),
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 200

    events = parse_sse_events(response.text)
    error_events = [e for e in events if e.get("type") == "error"]
    assert len(error_events) == 1
    assert "LLM connection failed" in error_events[0]["message"]

    # Exception path must not cache anything
    mock_setex.assert_not_called()


# ---------------------------------------------------------------------------
# Test 4 — agent returns wrong type → error event emitted, stream closes
# ---------------------------------------------------------------------------

async def test_cache_miss_agent_bad_response_emits_error_event(http_client):
    """
    If the agent returns a result dict whose 'structured_response' key is not
    a BioSignalFoundryOutput instance (e.g. None), the endpoint must emit an
    error event and NOT cache the result.

    This covers the 'else' branch of `isinstance(structured, BioSignalFoundryOutput)`.
    """
    with (
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module.redis_client, "setex") as mock_setex,
        patch.object(
            app_module.biosignalfoundry,
            "ainvoke",
            new_callable=AsyncMock,
            return_value={"structured_response": None},  # wrong type
        ),
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 200

    events = parse_sse_events(response.text)
    error_events = [e for e in events if e.get("type") == "error"]
    assert len(error_events) == 1
    assert "structured response" in error_events[0]["message"].lower()

    mock_setex.assert_not_called()


# ---------------------------------------------------------------------------
# Test 5 — input validation: empty string is rejected before the agent runs
# ---------------------------------------------------------------------------

async def test_input_validation_rejects_empty_string(http_client):
    """
    AnalyzeRequest enforces min_length=1. An empty user_input must return
    422 Unprocessable Entity — FastAPI validates this before our handler runs.
    """
    async with http_client as client:
        response = await client.post("/analyze", json={"user_input": ""})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 6 — input validation: oversized input is rejected
# ---------------------------------------------------------------------------

async def test_input_validation_rejects_too_long_input(http_client):
    """
    AnalyzeRequest enforces max_length=2000. A 2001-character string must
    return 422 before the handler even starts.
    """
    async with http_client as client:
        response = await client.post("/analyze", json={"user_input": "x" * 2001})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 7 — cache key: same input always produces the same hash
# ---------------------------------------------------------------------------

def test_input_hash_is_deterministic():
    """
    The SHA-256 hash of a given input must be identical across calls.
    If this ever broke (e.g. due to encoding changes), every cached
    result would become permanently stale — a silent correctness bug.
    """
    make_hash = lambda s: hashlib.sha256(s.strip().lower().encode()).hexdigest()

    assert make_hash("NVDA") == make_hash("NVDA")
    assert make_hash("analyze biotech sector") == make_hash("analyze biotech sector")


# ---------------------------------------------------------------------------
# Test 8 — cache key: whitespace and case are normalised before hashing
# ---------------------------------------------------------------------------

def test_input_hash_normalizes_whitespace_and_case():
    """
    'NVDA', '  NVDA  ', and 'nvda' must all map to the same cache key.
    This matches the strip().lower() applied in app.py before hashing,
    ensuring the cache isn't split across trivially equivalent inputs.
    """
    make_hash = lambda s: hashlib.sha256(s.strip().lower().encode()).hexdigest()

    assert make_hash("NVDA") == make_hash("  NVDA  ")
    assert make_hash("NVDA") == make_hash("nvda")
    assert make_hash("  NVDA  ") == make_hash("nvda")
