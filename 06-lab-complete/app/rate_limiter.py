"""Redis-backed sliding-window rate limiter."""
import time
import uuid

from fastapi import HTTPException

from app.config import settings
from app.redis_store import client


def check_rate_limit(user_id: str) -> dict[str, int]:
    now = time.time()
    window_start = now - settings.rate_limit_window_seconds
    key = f"rate:{user_id}"

    with client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        _, current = pipe.execute()

    if current >= settings.rate_limit_per_minute:
        oldest = client.zrange(key, 0, 0, withscores=True)
        retry_after = settings.rate_limit_window_seconds
        if oldest:
            retry_after = max(1, int(oldest[0][1] + settings.rate_limit_window_seconds - now) + 1)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    with client.pipeline(transaction=True) as pipe:
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        pipe.expire(key, settings.rate_limit_window_seconds + 1)
        pipe.execute()

    return {
        "limit": settings.rate_limit_per_minute,
        "remaining": settings.rate_limit_per_minute - current - 1,
    }
