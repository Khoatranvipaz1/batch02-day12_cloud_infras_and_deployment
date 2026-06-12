# Lab 12 — Complete Production Agent

Kết hợp TẤT CẢ những gì đã học trong 1 project hoàn chỉnh.

## Checklist Deliverable

- [x] Dockerfile (multi-stage, < 500 MB)
- [x] docker-compose.yml (agent + redis)
- [x] .dockerignore
- [x] Health check endpoint (`GET /health`)
- [x] Readiness endpoint (`GET /ready`)
- [x] API Key authentication
- [x] Rate limiting
- [x] Cost guard
- [x] Config từ environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Public URL ready (Railway / Render config)

---

## Cấu Trúc

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — kết hợp tất cả
│   ├── config.py       # 12-factor config
│   ├── auth.py         # API Key authentication
│   ├── redis_store.py  # Redis connection + conversation history
│   ├── rate_limiter.py # Rate limiting
│   └── cost_guard.py   # Budget protection
├── utils/
│   └── mock_llm.py     # Mock LLM chạy offline
├── tests/
│   └── test_app.py     # API/security/reliability tests
├── Dockerfile          # Multi-stage, production-ready
├── docker-compose.yml  # Full stack
├── railway.toml        # Deploy Railway
├── render.yaml         # Deploy Render
├── .env.example        # Template
├── .dockerignore
├── requirements.txt
└── requirements-dev.txt
```

---

## Chạy Local

```bash
# 1. Chạy agent + Redis
docker compose up --build

# 2. Test health/readiness
curl http://localhost:8000/health
curl http://localhost:8000/ready

# 3. Test endpoint có authentication
curl -H "X-API-Key: dev-key-change-me" \
     -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"user_id":"demo","question":"What is deployment?"}'
```

---

## Deploy Railway (< 5 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway variables set AGENT_API_KEY=your-secret-key
railway variables set REDIS_URL=your-redis-url
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
railway up

# Nhận public URL!
railway domain
```

---

## Deploy Render

1. Push repo lên GitHub
2. Render Dashboard → New → Blueprint
3. Connect repo → Render đọc `render.yaml`
4. Set secrets: `AGENT_API_KEY`, `REDIS_URL`
5. Deploy → Nhận URL!

Nếu deploy từ repository Day 12 đầy đủ, đặt root directory của service thành
`06-lab-complete`. Cách đơn giản nhất để nộp bài là dùng chính nội dung folder
`06-lab-complete` làm root của một repository submission riêng.

---

## Kiểm Tra Production Readiness

```bash
pip install -r requirements-dev.txt
python check_production_ready.py
python -m pytest -q
```

Script này kiểm tra tất cả items trong checklist và báo cáo những gì còn thiếu.
