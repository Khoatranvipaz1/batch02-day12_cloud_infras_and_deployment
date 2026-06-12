# Day 12 Lab - Mission Answers

**Student Name:** Trần Văn Khoa

**Student ID:** 2A202600827

**Date:** 12/06/2026

Phan tich chi tiet source `develop` va `production`:
[DEVELOP_VS_PRODUCTION.md](DEVELOP_VS_PRODUCTION.md).

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. API key is hardcoded in source code.
2. Server port is hardcoded.
3. Debug mode is always enabled.
4. There is no health-check endpoint.
5. The process does not handle graceful shutdown.
6. Logs use `print()` instead of structured logging.
7. Configuration is not separated from code.

### Exercise 1.2: Develop version

The develop source was reviewed and run pattern was verified. It exposes
`POST /ask` but is intentionally unsuitable for production because it binds to
localhost, enables reload, and contains hardcoded credentials.

### Exercise 1.3: Comparison

| Feature | Develop | Production | Why it matters |
|---|---|---|---|
| Config | Hardcoded | Environment variables | One image can run in different environments |
| Secrets | Stored in code | Injected at runtime | Prevents secrets from leaking through Git |
| Port | Fixed | Reads `PORT` | Required by cloud platforms |
| Health | Missing | `/health` and `/ready` | Enables monitoring and safe traffic routing |
| Logging | Plain text | Structured JSON | Easier to search and process |
| Shutdown | Abrupt | Uvicorn/FastAPI lifespan | Allows cleanup before the process exits |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: Python slim runtime (`python:3.11-slim`).
2. Working directory: `/app` in the final image.
3. Requirements are copied first so Docker can reuse the dependency layer when
   application code changes.
4. `CMD` provides a default command that can be overridden. `ENTRYPOINT`
   defines the executable that the container always runs.

### Exercise 2.3: Multi-stage build

The builder stage installs dependencies. The runtime stage copies only the
installed packages and application source. Build tools and temporary files are
not included in the final image.

The final image was built successfully and measured `187 MB`, below the
required 500 MB limit.

Measured image comparison:

| Image | Size |
|---|---:|
| Module 02 develop | 1,149,322,478 bytes (about 1.15 GB) |
| Final production image | 187,249,852 bytes (about 187 MB) |

The final image is approximately `83.7%` smaller than the develop image.

### Exercise 2.4: Architecture

```text
Client -> Agent (FastAPI, port 8000) -> Redis (port 6379)
```

Redis stores conversation history, rate-limit windows, and monthly usage. This
allows multiple agent workers or instances to share the same state.

Local verification:

```text
docker compose config: passed
agent container: healthy
redis container: healthy
```

## Part 3: Cloud Deployment

### Railway

The project includes `06-lab-complete/railway.toml`. Deployment requires:

- `ENVIRONMENT=production`
- `AGENT_API_KEY=<strong secret>`
- `REDIS_URL=<managed Redis URL>`

Public URL and deployment screenshot are pending cloud account access.

### Render comparison

Railway uses `railway.toml` and CLI-oriented deployment. Render uses
`render.yaml` as a Blueprint. Both inject environment variables at runtime and
use `/health` for health checks.

Cloud Run is more configurable and suitable for mature production workloads,
but requires additional GCP and CI/CD setup.

## Part 4: API Security

### API key authentication

`app/auth.py` reads `X-API-Key` and compares it with `AGENT_API_KEY` using
constant-time comparison. Missing or invalid credentials return `401`.

Verified locally:

```text
Missing API key: 401
Invalid API key: 401
Valid API key: 200
Invalid request body: 422
```

### JWT

JWT is useful when each user needs an identity, roles, and token expiry. This
lab's final public service uses the required API-key flow. OAuth2 would be more
appropriate for delegated login through an identity provider.

### Rate limiting

`app/rate_limiter.py` implements a Redis sorted-set sliding window:

1. Remove timestamps older than 60 seconds.
2. Count active requests.
3. Return `429` when the count reaches 10.
4. Otherwise record the new request with an expiring Redis key.

Local integration test returned `429` on the request after the configured
10-request window was exhausted.

### Cost guard

`app/cost_guard.py` estimates token cost and stores monthly usage in Redis under
`budget:<user_id>:<YYYY-MM>`. A request that would exceed 10 USD returns `402`.

The `402` response was verified by setting the user's monthly Redis usage to
the configured limit and calling `/ask`.

## Part 5: Scaling and Reliability

### Health and readiness

- `/health` is a liveness endpoint and always describes the process state.
- `/ready` checks Redis and returns `503` when the required backing service is
  unavailable.

### Graceful shutdown

Uvicorn handles `SIGTERM`. FastAPI's lifespan shutdown phase logs a
`graceful_shutdown` event and closes the Redis client.

### Stateless design

Application workers do not store user conversation, rate limits, or budget in
process memory. Redis is the shared backing service, so a later request can be
handled by another worker without losing user state.

### Load balancing

The Docker image starts two Uvicorn workers. Both workers use the same Redis
service. The same design can scale to more cloud instances behind the
platform's load balancer.

The response includes an `instance_id`, and conversation history remained
available through Redis across requests.

### Verification results

```text
Production readiness checker: 22/22 passed
Pytest: 6/6 passed
Python compile: passed
Docker Compose config: passed
Docker image: 187 MB
Docker runtime: agent and Redis healthy
Live API: 200, 401, 402, and 429 responses verified
Graceful shutdown: SIGTERM verified for both Uvicorn workers
```
