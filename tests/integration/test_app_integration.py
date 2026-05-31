"""
Integration tests for POST /analyze with a live Redis.

These tests verify that app.py correctly reads from and writes to Redis
using real network I/O — not mocks.  The LLM/agent is still mocked because
we are testing the app ↔ Redis boundary specifically, not the LLM.

What these tests prove that unit tests cannot:
  - The cache key written by app.py is exactly the key that get() finds.
  - The JSON stored in Redis is well-formed and retrievable by a second request.
  - The agent is truly skipped on a cache hit — not just in mocked logic.

Run with:  pytest tests/integration/
Requires:  docker run -p 6379:6379 redis:7
"""

import hashlib
import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import app as app_module
from app import app
from src.biosignalfoundry import BioSignalFoundryOutput
from src.core.redis_client import redis_client

TEST_INPUT = "integration test analyze NVDA"

STRUCTURED_RESULT = BioSignalFoundryOutput(
    ticker="NVDA",
    decision="Buy",
    confidence=85,
    reasoning="Strong pipeline",
)


def make_cache_key(user_input: str) -> str:
    """Mirrors the hashing logic in app.py exactly."""
    h = hashlib.sha256(user_input.strip().lower().encode()).hexdigest()
    return f"biosignalfoundry:analyze:{h}"


@pytest.fixture
def http_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture(autouse=True)
def clean_test_key():
    """Delete the test cache key before and after each test for a clean slate."""
    key = make_cache_key(TEST_INPUT)
    redis_client.delete(key)
    yield
    redis_client.delete(key)


def parse_sse_result(text: str) -> dict | None:
    """Return the first 'result' event from an SSE response body, or None."""
    for line in text.splitlines():
        if line.startswith("data: "):
            event = json.loads(line.removeprefix("data: "))
            if event.get("type") == "result":
                return event
    return None


# ---------------------------------------------------------------------------
# Test 1 — cache miss writes the result to real Redis
# ---------------------------------------------------------------------------


async def test_cache_miss_writes_result_to_redis(http_client):
    """
    On a cache miss the agent runs and app.py must write the result to Redis.
    After the request completes, the key must exist in real Redis with a
    well-formed JSON payload.

    Unit tests verify setex is called; this test verifies the key is actually
    readable from Redis — proving the key format, TTL argument, and
    serialization are all correct end-to-end.
    """
    with patch.object(
        app_module.biosignalfoundry,
        "ainvoke",
        new_callable=AsyncMock,
        return_value={"structured_response": STRUCTURED_RESULT},
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": TEST_INPUT})

    assert response.status_code == 200

    key = make_cache_key(TEST_INPUT)
    raw = redis_client.get(key)
    assert raw is not None, "app.py must write the result to Redis after a cache miss"

    cached = json.loads(raw)
    assert cached["type"] == "result"
    assert cached["data"]["ticker"] == "NVDA"
    assert cached["data"]["decision"] == "Buy"


# ---------------------------------------------------------------------------
# Test 2 — second identical request is served from Redis; agent not called again
# ---------------------------------------------------------------------------


async def test_second_request_is_served_from_cache(http_client):
    """
    A second POST /analyze with the same input must be served from Redis.
    The agent must be called exactly once across both requests.

    This is the core caching contract: expensive LLM calls happen once,
    subsequent identical queries are free.  Unit tests verify the logic in
    isolation; this test proves it against a real Redis instance.
    """
    with patch.object(
        app_module.biosignalfoundry,
        "ainvoke",
        new_callable=AsyncMock,
        return_value={"structured_response": STRUCTURED_RESULT},
    ) as mock_ainvoke:
        async with http_client as client:
            first = await client.post("/analyze", json={"user_input": TEST_INPUT})
            second = await client.post("/analyze", json={"user_input": TEST_INPUT})

    assert first.status_code == 200
    assert second.status_code == 200

    mock_ainvoke.assert_called_once()

    first_event = parse_sse_result(first.text)
    second_event = parse_sse_result(second.text)

    assert first_event is not None
    assert second_event is not None
    assert first_event["data"]["ticker"] == second_event["data"]["ticker"]


# ---------------------------------------------------------------------------
# Test 3 — cached SSE payload has the full expected shape
# ---------------------------------------------------------------------------


async def test_cached_payload_has_correct_shape(http_client):
    """
    The event served from the Redis cache must contain all four fields that
    BioSignalFoundryOutput defines: ticker, decision, confidence, reasoning.

    Catches serialization bugs where data round-trips through Redis but comes
    back with missing keys or wrong types (e.g. confidence serialized as string).
    """
    with patch.object(
        app_module.biosignalfoundry,
        "ainvoke",
        new_callable=AsyncMock,
        return_value={"structured_response": STRUCTURED_RESULT},
    ):
        async with http_client as client:
            await client.post("/analyze", json={"user_input": TEST_INPUT})
            cached_response = await client.post("/analyze", json={"user_input": TEST_INPUT})

    event = parse_sse_result(cached_response.text)
    assert event is not None, "Expected a 'result' SSE event in the cached response"

    data = event["data"]
    assert data["ticker"] == "NVDA"
    assert data["decision"] == "Buy"
    assert isinstance(data["confidence"], int)
    assert isinstance(data["reasoning"], str)
