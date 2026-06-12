"""Redis connection and conversation storage."""
import json
import logging
from datetime import datetime, timezone

import redis
from redis.exceptions import RedisError

from app.config import settings


logger = logging.getLogger(__name__)
client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def ping() -> bool:
    try:
        return bool(client.ping())
    except RedisError:
        return False


def require_redis() -> None:
    if not ping():
        raise RedisError("Redis is not available")


def load_history(user_id: str) -> list[dict[str, str]]:
    values = client.lrange(f"history:{user_id}", 0, -1)
    return [json.loads(value) for value in values]


def append_history(user_id: str, role: str, content: str) -> None:
    key = f"history:{user_id}"
    message = json.dumps(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    with client.pipeline(transaction=True) as pipe:
        pipe.rpush(key, message)
        pipe.ltrim(key, -settings.history_max_messages, -1)
        pipe.expire(key, settings.history_ttl_seconds)
        pipe.execute()


def close() -> None:
    client.close()
