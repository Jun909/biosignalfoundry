import pytest
from redis import ConnectionError as RedisConnectionError

from src.core.redis_client import redis_client


@pytest.fixture(autouse=True)
def require_redis():
    """Skip any integration test when Redis is not reachable."""
    try:
        redis_client.ping()
    except RedisConnectionError:
        pytest.skip(
            "Redis not available — start one with: docker run -p 6379:6379 redis:7"
        )


@pytest.fixture
def tracked_keys():
    """Yields a mutable list. Every key appended to it is deleted after the test."""
    keys: list[str] = []
    yield keys
    if keys:
        redis_client.delete(*keys)
