"""
Tests for src/core/rate_limiter.py.

Mocking strategy
-----------------
redis_client.pipeline() is patched to return a fake pipeline whose execute()
returns canned [count, expire_ok] pairs — this is the real Redis contract
(INCR returns the new count, EXPIRE returns True/False), so tests don't need
a live Redis server.
"""

from unittest.mock import MagicMock, patch

from src.core.rate_limiter import (check_and_consume_daily_budget,
                                   check_rate_limit)


def _fake_pipeline_factory(execute_results):
    """Return a `pipeline()` replacement whose successive calls yield each
    result in execute_results in order — one entry per _incr_with_expiry
    call made during the test.
    """
    calls = iter(execute_results)

    def _pipeline():
        pipe = MagicMock()
        pipe.execute.return_value = next(calls)
        return pipe

    return _pipeline


def test_check_rate_limit_allows_under_both_limits():
    with patch("src.core.rate_limiter.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = _fake_pipeline_factory([[1, True], [1, True]])
        allowed, retry_after = check_rate_limit("1.2.3.4", per_minute=5, per_day=50)

    assert allowed is True
    assert retry_after == 0


def test_check_rate_limit_blocks_when_minute_limit_exceeded():
    with patch("src.core.rate_limiter.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = _fake_pipeline_factory([[6, True]])
        allowed, retry_after = check_rate_limit("1.2.3.4", per_minute=5, per_day=50)

    assert allowed is False
    assert 0 <= retry_after <= 60


def test_check_rate_limit_blocks_when_day_limit_exceeded():
    with patch("src.core.rate_limiter.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = _fake_pipeline_factory(
            [[1, True], [51, True]]
        )
        allowed, retry_after = check_rate_limit("1.2.3.4", per_minute=5, per_day=50)

    assert allowed is False
    assert 0 <= retry_after <= 86400


def test_check_and_consume_daily_budget_allows_under_cap():
    with patch("src.core.rate_limiter.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = _fake_pipeline_factory([[100, True]])
        assert check_and_consume_daily_budget(cap=500) is True


def test_check_and_consume_daily_budget_blocks_over_cap():
    with patch("src.core.rate_limiter.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = _fake_pipeline_factory([[501, True]])
        assert check_and_consume_daily_budget(cap=500) is False
