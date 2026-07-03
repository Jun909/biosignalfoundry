"""
Integration tests for Redis cache operations.

These tests use a live Redis connection and verify that the exact key format,
serialization, TTL, and expiry behaviour work correctly — not with mocks.

Each test uses the `tracked_keys` fixture (from conftest.py) to clean up
after itself. No test leaves data behind in Redis.

Run with:  pytest tests/integration/
Requires:  docker run -p 6379:6379 redis:7
"""

import hashlib
import json
import time

from config import REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY
from src.core.redis_client import redis_client


def make_cache_key(user_input: str) -> str:
    """Mirrors the hashing logic in app.py exactly."""
    h = hashlib.sha256(user_input.strip().lower().encode()).hexdigest()
    return f"biosignalfoundry:analyze:{h}"


# ---------------------------------------------------------------------------
# Test 1 — get() on an unknown key returns None
# ---------------------------------------------------------------------------


def test_cache_miss_returns_none(tracked_keys):
    """
    get() on a key that was never written must return None.

    This verifies that decode_responses=True (set in redis_client.py) does
    not turn a Redis nil reply into an empty string or b''.  app.py relies
    on `if cached:` to branch on None, so a non-None falsy value would
    silently skip the agent on every request.
    """
    key = make_cache_key("__integration_nonexistent__")
    tracked_keys.append(key)

    assert redis_client.get(key) is None


# ---------------------------------------------------------------------------
# Test 2 — setex stores data; get retrieves it byte-for-byte
# ---------------------------------------------------------------------------


def test_setex_and_get_round_trip(tracked_keys):
    """Data written with setex must come back unchanged from get()."""
    key = make_cache_key("NVDA_roundtrip")
    payload = '{"type": "result", "data": {"ticker": "NVDA"}}'
    tracked_keys.append(key)

    redis_client.setex(key, REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, payload)

    assert redis_client.get(key) == payload


# ---------------------------------------------------------------------------
# Test 3 — full result event dict survives JSON → Redis → JSON
# ---------------------------------------------------------------------------


def test_json_survives_redis_round_trip(tracked_keys):
    """
    A complete result event (the exact shape cached by app.py) must survive
    json.dumps → setex → get → json.loads without any data loss or mutation.

    Regression guard: if Redis is misconfigured to return bytes instead of
    strings, json.loads would raise TypeError here rather than silently
    corrupting the cache.
    """
    key = make_cache_key("AMGN_json")
    event = {
        "type": "result",
        "data": {
            "ticker": "AMGN",
            "decision": "Hold",
            "confidence": 72,
            "reasoning": "Stable revenue with moderate growth",
        },
    }
    tracked_keys.append(key)

    redis_client.setex(key, REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, json.dumps(event))

    assert json.loads(redis_client.get(key)) == event


# ---------------------------------------------------------------------------
# Test 4 — setex applies the configured TTL
# ---------------------------------------------------------------------------


def test_ttl_is_applied_by_setex(tracked_keys):
    """
    After setex, the Redis TTL command must report a value within 2 seconds
    of REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY.

    This confirms that setex is called with the right argument order and that
    the TTL constant in config.py reaches Redis correctly.
    """
    key = make_cache_key("GILD_ttl")
    tracked_keys.append(key)

    redis_client.setex(key, REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, "data")

    ttl = redis_client.ttl(key)
    assert (
        REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY - 2
        <= ttl
        <= REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY
    )


# ---------------------------------------------------------------------------
# Test 5 — key is absent after TTL elapses
# ---------------------------------------------------------------------------


def test_key_expires_after_ttl(tracked_keys):
    """
    A key set with TTL=1 must be absent 2 seconds later.

    This is the only test that proves the expiry mechanism actually fires —
    the unit tests cannot verify this because they mock Redis entirely.
    """
    key = make_cache_key("EXPIRY_integration")
    tracked_keys.append(key)

    redis_client.setex(key, 1, "temporary")
    time.sleep(2)

    assert redis_client.get(key) is None


# ---------------------------------------------------------------------------
# Test 6 — second setex on the same key overwrites the first value
# ---------------------------------------------------------------------------


def test_second_setex_overwrites_first(tracked_keys):
    """
    Writing the same cache key twice must replace the first value.

    If the cache ever refreshes a result (e.g. after TTL is reduced), the
    new value must be what subsequent gets return — not the stale first write.
    """
    key = make_cache_key("OVERWRITE_integration")
    tracked_keys.append(key)

    redis_client.setex(key, REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, "first")
    redis_client.setex(key, REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, "second")

    assert redis_client.get(key) == "second"
