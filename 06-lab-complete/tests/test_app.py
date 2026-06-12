import fnmatch

import fakeredis
from fastapi.testclient import TestClient

from app.config import settings
from app import cost_guard, rate_limiter, redis_store
import app.main as main_module


fake_redis = fakeredis.FakeRedis(decode_responses=True)
redis_store.client = fake_redis
rate_limiter.client = fake_redis
cost_guard.client = fake_redis

from app.main import app  # noqa: E402


def _scan_delete(pattern: str) -> None:
    for key in fake_redis.scan_iter("*"):
        if fnmatch.fnmatch(key, pattern):
            fake_redis.delete(key)


def test_health_and_ready():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200


def test_authentication_and_validation():
    with TestClient(app) as client:
        assert client.post("/ask", json={"question": "Hello"}).status_code == 401
        assert client.post(
            "/ask",
            headers={"X-API-Key": "wrong-key"},
            json={"question": "Hello"},
        ).status_code == 401
        response = client.post(
            "/ask",
            headers={"X-API-Key": settings.agent_api_key},
            json={"user_id": "auth-test", "question": "Hello"},
        )
        assert response.status_code == 200
        assert client.post(
            "/ask",
            headers={"X-API-Key": settings.agent_api_key},
            json={"user_id": "auth-test"},
        ).status_code == 422


def test_ready_returns_503_when_redis_is_down(monkeypatch):
    monkeypatch.setattr(main_module, "ping", lambda: False)
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 503


def test_conversation_history():
    _scan_delete("history:conversation-test")
    headers = {"X-API-Key": settings.agent_api_key}
    with TestClient(app) as client:
        first = client.post(
            "/ask",
            headers=headers,
            json={"user_id": "conversation-test", "question": "My name is Alice"},
        )
        second = client.post(
            "/ask",
            headers=headers,
            json={"user_id": "conversation-test", "question": "What is my name?"},
        )
    assert first.status_code == 200
    assert second.status_code == 200
    assert "Alice" in second.json()["answer"]


def test_rate_limit():
    user_id = "rate-test"
    _scan_delete(f"rate:{user_id}")
    original_limit = settings.rate_limit_per_minute
    settings.rate_limit_per_minute = 2
    headers = {"X-API-Key": settings.agent_api_key}
    try:
        with TestClient(app) as client:
            for _ in range(2):
                assert client.post(
                    "/ask",
                    headers=headers,
                    json={"user_id": user_id, "question": "Hello"},
                ).status_code == 200
            assert client.post(
                "/ask",
                headers=headers,
                json={"user_id": user_id, "question": "Hello"},
            ).status_code == 429
    finally:
        settings.rate_limit_per_minute = original_limit


def test_cost_guard():
    user_id = "budget-test"
    fake_redis.set(cost_guard._usage_key(user_id), settings.monthly_budget_usd)
    with TestClient(app) as client:
        response = client.post(
            "/ask",
            headers={"X-API-Key": settings.agent_api_key},
            json={"user_id": user_id, "question": "Hello"},
        )
    assert response.status_code == 402
