"""Redis-backed monthly LLM budget protection."""
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings
from app.redis_store import client


INPUT_PRICE_PER_1K = 0.00015
OUTPUT_PRICE_PER_1K = 0.0006


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * INPUT_PRICE_PER_1K
        + output_tokens / 1000 * OUTPUT_PRICE_PER_1K
    )


def _usage_key(user_id: str) -> str:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return f"budget:{user_id}:{month}"


def check_budget(user_id: str, estimated_cost: float = 0.0) -> float:
    current = float(client.get(_usage_key(user_id)) or 0.0)
    if current + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Monthly budget exceeded",
                "used_usd": round(current, 6),
                "budget_usd": settings.monthly_budget_usd,
            },
        )
    return current


def record_usage(user_id: str, input_tokens: int, output_tokens: int) -> float:
    cost = estimate_cost(input_tokens, output_tokens)
    key = _usage_key(user_id)
    with client.pipeline(transaction=True) as pipe:
        pipe.incrbyfloat(key, cost)
        pipe.expire(key, 32 * 24 * 60 * 60)
        new_value, _ = pipe.execute()
    return float(new_value)


def get_usage(user_id: str) -> dict[str, float | str]:
    used = float(client.get(_usage_key(user_id)) or 0.0)
    return {
        "user_id": user_id,
        "used_usd": round(used, 6),
        "budget_usd": settings.monthly_budget_usd,
        "remaining_usd": round(max(0.0, settings.monthly_budget_usd - used), 6),
    }
