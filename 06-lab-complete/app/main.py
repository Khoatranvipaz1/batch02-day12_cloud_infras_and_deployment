"""Production-ready FastAPI agent for the Day 12 deployment lab."""
import json
import logging
import signal
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, estimate_cost, get_usage, record_usage
from app.rate_limiter import check_rate_limit
from app.redis_store import append_history, close, load_history, ping, require_redis
from utils.mock_llm import ask as llm_ask


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("agent")
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(
    logging.DEBUG if settings.debug else getattr(logging, settings.log_level, logging.INFO)
)
logger.propagate = False

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]
GRACEFUL_SHUTDOWN_SIGNAL = signal.SIGTERM
request_count = 0
error_count = 0


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(
        json.dumps(
            {
                "event": "startup",
                "version": settings.app_version,
                "instance_id": INSTANCE_ID,
                "redis_ready": ping(),
            }
        )
    )
    yield
    logger.info(
        json.dumps(
            {
                "event": "graceful_shutdown",
                "signal": GRACEFUL_SHUTDOWN_SIGNAL.name,
            }
        )
    )
    close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global request_count, error_count
    started_at = time.perf_counter()
    request_count += 1
    try:
        response: Response = await call_next(request)
    except Exception:
        error_count += 1
        logger.exception("Unhandled request error")
        raise

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    logger.info(
        json.dumps(
            {
                "event": "request",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
            }
        )
    )
    return response


class AskRequest(BaseModel):
    user_id: str = Field(default="default", min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    model: str
    timestamp: str
    instance_id: str


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "ask": "POST /ask with X-API-Key",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "dependencies": {"redis": "up" if ping() else "down"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def ready():
    if not ping():
        raise HTTPException(status_code=503, detail="Redis is not ready")
    return {"status": "ready", "instance_id": INSTANCE_ID}


@app.post("/ask", response_model=AskResponse)
def ask_agent(body: AskRequest, _api_key: str = Depends(verify_api_key)):
    try:
        require_redis()
        check_rate_limit(body.user_id)
        input_tokens = max(1, len(body.question.split()) * 2)
        check_budget(body.user_id, estimate_cost(input_tokens, 0))

        history = load_history(body.user_id)
        answer = llm_ask(body.question, history)
        output_tokens = max(1, len(answer.split()) * 2)
        check_budget(body.user_id, estimate_cost(input_tokens, output_tokens))

        append_history(body.user_id, "user", body.question)
        append_history(body.user_id, "assistant", answer)
        record_usage(body.user_id, input_tokens, output_tokens)
    except HTTPException:
        raise
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from exc

    return AskResponse(
        user_id=body.user_id,
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
        instance_id=INSTANCE_ID,
    )


@app.get("/usage/{user_id}")
def usage(user_id: str, _api_key: str = Depends(verify_api_key)):
    try:
        require_redis()
        return get_usage(user_id)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from exc


@app.get("/metrics")
def metrics(_api_key: str = Depends(verify_api_key)):
    return {
        "instance_id": INSTANCE_ID,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "requests": request_count,
        "errors": error_count,
    }
