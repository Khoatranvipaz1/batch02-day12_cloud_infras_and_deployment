# Deployment Information

**Student Name:** Trần Văn Khoa

**Student ID:** 2A202600827

**Date:** 12/06/2026

## Status

Deployment is pending cloud account authentication.

## Public URL

```text
PENDING_RAILWAY_OR_RENDER_URL
```

## Recommended Platform

Railway with a managed Redis service.

## Required Environment Variables

```text
ENVIRONMENT=production
AGENT_API_KEY=<strong-random-secret>
REDIS_URL=<managed-redis-connection-url>
RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0
LOG_LEVEL=INFO
```

`OPENAI_API_KEY` is optional because the lab currently uses an offline mock LLM.

## Railway Deployment

```bash
cd 06-lab-complete
railway login
railway init
railway variables set ENVIRONMENT=production
railway variables set AGENT_API_KEY=<strong-random-secret>
railway variables set REDIS_URL=<managed-redis-connection-url>
railway variables set LOG_LEVEL=INFO
railway up
railway domain
```

When deploying the complete Day 12 repository, configure the service root
directory as `06-lab-complete`. Alternatively, publish the contents of
`06-lab-complete` as the root of a separate submission repository.

## Public Test Commands

Replace `$URL` and `$KEY` after deployment.

```bash
curl "$URL/health"
curl "$URL/ready"

# Expected: 401
curl -X POST "$URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","question":"Hello"}'

# Expected: 200
curl -X POST "$URL/ask" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","question":"Hello"}'

# Eventually expected: 429
for i in $(seq 1 15); do
  curl -X POST "$URL/ask" \
    -H "X-API-Key: $KEY" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"rate-demo","question":"test"}'
done
```

## Screenshots

- `screenshots/dashboard.png`: pending
- `screenshots/running.png`: pending
- `screenshots/test.png`: pending
