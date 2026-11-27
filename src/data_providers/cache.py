"""Redis response cache shared by providers without a built-in one (OpenFDA, SEC)."""

import json
from collections.abc import Callable
from typing import Any

import structlog
from redis.exceptions import RedisError

from src.core.redis_client import redis_client

logger = structlog.get_logger()


def cached_call(key: str, ttl: int, fetch: Callable[[], dict[str, Any]]) -> dict:
    """Return the cached response for ``key`` or call ``fetch`` and cache it.

    Only ``ok`` responses are cached, so a transient failure is not served as the
    answer for the whole TTL. Redis errors are treated as a cache miss.
    """
    try:
        hit = redis_client.get(key)
    except RedisError as e:
        logger.warning("cache read failed, treating as cache miss", error=str(e))
        hit = None
    if hit:
        return json.loads(hit)  # type: ignore[arg-type]

    result = fetch()
    if result.get("ok"):
        try:
            redis_client.setex(key, ttl, json.dumps(result, default=str))
        except RedisError as e:
            logger.warning("cache write failed, skipping cache", error=str(e))
    return result
