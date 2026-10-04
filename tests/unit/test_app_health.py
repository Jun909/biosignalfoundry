"""
Tests for GET /health and GET /ready in app.py.

Mocking strategy
----------------
redis_client.ping is patched on the module-level object in app.py, same seam
used in test_app_analyze.py.
"""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

import app as app_module
from app import app


@pytest.fixture
def http_client():
    """Async HTTPX client wired to the FastAPI app."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# /health — liveness: always ok, no dependency checks
# ---------------------------------------------------------------------------


async def test_health_returns_ok(http_client):
    async with http_client as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /ready — readiness: reflects Redis reachability
# ---------------------------------------------------------------------------


async def test_ready_returns_ok_when_redis_reachable(http_client):
    with patch.object(app_module.redis_client, "ping", return_value=True):
        async with http_client as client:
            response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_returns_503_when_redis_unreachable(http_client):
    """
    A Redis outage must surface as a 503 on /ready so load balancers/orchestrators
    stop routing traffic here, instead of the process claiming to be healthy while
    /analyze would fail on its first redis_client call.
    """
    with patch.object(
        app_module.redis_client, "ping", side_effect=ConnectionError("down")
    ):
        async with http_client as client:
            response = await client.get("/ready")

    assert response.status_code == 503
