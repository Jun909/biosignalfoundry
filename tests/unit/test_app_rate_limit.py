"""
Tests for rate limiting and daily budget cap enforcement on POST /analyze.

Mocking strategy
-----------------
check_rate_limit / check_and_consume_daily_budget (imported into app.py from
src.core.rate_limiter) are patched directly — the same seam
test_app_analyze.py bypasses via its autouse fixture is exercised here
instead. redis_client.get/setex and biosignalfoundry.ainvoke are mocked as
in test_app_analyze.py so no real cache or agent work happens.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from redis.exceptions import ConnectionError as RedisConnectionError

import app as app_module
from app import app
from src.biosignalfoundry import BioSignalFoundryOutput

STRUCTURED_RESULT = BioSignalFoundryOutput(
    ticker="NVDA",
    decision="Buy",
    confidence=85,
    reasoning="Strong pipeline",
)


@pytest.fixture
def http_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# Rate limit
# ---------------------------------------------------------------------------


async def test_rate_limit_exceeded_returns_429_with_retry_after(http_client):
    with (
        patch.object(app_module, "check_rate_limit", return_value=(False, 42)),
        patch.object(
            app_module.biosignalfoundry, "ainvoke", new_callable=AsyncMock
        ) as mock_ainvoke,
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 429
    assert response.headers["retry-after"] == "42"
    mock_ainvoke.assert_not_called()


async def test_rate_limit_check_failure_fails_open(http_client):
    """If Redis is down, rate limiting must not block legitimate traffic —
    caching already degrades gracefully the same way; rate limiting should
    fail the same direction.
    """
    with (
        patch.object(
            app_module, "check_rate_limit", side_effect=RedisConnectionError("down")
        ),
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module.redis_client, "setex"),
        patch.object(app_module, "check_and_consume_daily_budget", return_value=True),
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


# ---------------------------------------------------------------------------
# Daily budget cap
# ---------------------------------------------------------------------------


async def test_daily_budget_cap_reached_returns_503_on_cache_miss(http_client):
    with (
        patch.object(app_module, "check_rate_limit", return_value=(True, 0)),
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module, "check_and_consume_daily_budget", return_value=False),
        patch.object(
            app_module.biosignalfoundry, "ainvoke", new_callable=AsyncMock
        ) as mock_ainvoke,
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 503
    mock_ainvoke.assert_not_called()


async def test_daily_budget_cap_not_checked_on_cache_hit(http_client):
    """Cache hits are free — the budget cap only guards non-cached agent
    runs, so it must not even be consulted when the cache already has the
    answer.
    """
    cached_payload = '{"type": "result", "data": {"ticker": "NVDA"}}'
    with (
        patch.object(app_module, "check_rate_limit", return_value=(True, 0)),
        patch.object(app_module.redis_client, "get", return_value=cached_payload),
        patch.object(app_module, "check_and_consume_daily_budget") as mock_budget_check,
    ):
        async with http_client as client:
            response = await client.post("/analyze", json={"user_input": "NVDA"})

    assert response.status_code == 200
    mock_budget_check.assert_not_called()


async def test_budget_check_failure_fails_open(http_client):
    with (
        patch.object(app_module, "check_rate_limit", return_value=(True, 0)),
        patch.object(app_module.redis_client, "get", return_value=None),
        patch.object(app_module.redis_client, "setex"),
        patch.object(
            app_module,
            "check_and_consume_daily_budget",
            side_effect=RedisConnectionError("down"),
        ),
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
