"""Redis-backed rate limiting and daily budget enforcement for /analyze.

Fixed-window counters via INCR+EXPIRE. Not a sliding window (a client can
burst across a window boundary), but it's sufficient for abuse/cost control
here and keeps this to a single round trip per check.
"""

import time

from src.core.redis_client import redis_client


def _incr_with_expiry(key: str, window_seconds: int) -> int:
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds, nx=True)
    count, _ = pipe.execute()

    return count


def check_rate_limit(client_ip: str, per_minute: int, per_day: int) -> tuple[bool, int]:
    """Check and consume one request against per-IP rate limits.

    Returns (allowed, retry_after_seconds). Raises redis.exceptions.RedisError
    on Redis failure so the caller can decide the fail-open/closed policy.
    """
    now = int(time.time())

    minute_count = _incr_with_expiry(
        f"biosignalfoundry:ratelimit:ip:{client_ip}:minute:{now // 60}", 60
    )
    if minute_count > per_minute:
        return False, 60 - (now % 60)

    day_count = _incr_with_expiry(
        f"biosignalfoundry:ratelimit:ip:{client_ip}:day:{now // 86400}", 86400
    )
    if day_count > per_day:
        return False, 86400 - (now % 86400)

    return True, 0


def check_and_consume_daily_budget(cap: int) -> bool:
    """Consume one unit of the global daily budget for non-cached /analyze runs.

    Returns True if under the cap, False if the cap has been reached. Raises
    redis.exceptions.RedisError on Redis failure so the caller can decide the
    fail-open/closed policy.
    """
    now = int(time.time())
    count = _incr_with_expiry(f"biosignalfoundry:budget:day:{now // 86400}", 86400)
    return count <= cap
