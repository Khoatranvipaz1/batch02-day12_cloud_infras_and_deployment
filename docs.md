# Day 12 Lab - Work Plan and Completion Checklist

Tai lieu nay la checklist lam viec chinh. Cap nhat trang thai ngay sau moi buoc
de tranh bo sot yeu cau cua lab va rubric cham diem.

## 1. Thu tu lam viec

1. Kiem tra source va rubric.
2. Hoan thien cau truc project trong `06-lab-complete/`.
3. Hoan thien API va business logic.
4. Hoan thien Docker va cau hinh deployment.
5. Chay static checker, unit test va Docker test.
6. Deploy len Railway hoac Render.
7. Test public URL va luu screenshot.
8. Hoan thien tai lieu nop bai.

## 2. Checklist source code

- [x] `app/main.py`: FastAPI entry point.
- [x] `app/config.py`: doc config tu environment variables.
- [x] `app/auth.py`: xac thuc header `X-API-Key`.
- [x] `app/redis_store.py`: ket noi Redis va luu conversation history.
- [x] `app/rate_limiter.py`: Redis sliding-window, mac dinh 10 request/phut.
- [x] `app/cost_guard.py`: Redis monthly budget, mac dinh 10 USD/user.
- [x] `utils/mock_llm.py`: mock LLM chay offline.
- [x] Khong hardcode secret production.
- [x] Structured JSON logging.
- [x] Graceful shutdown qua FastAPI lifespan/Uvicorn SIGTERM handling.

## 3. Checklist API

- [x] `GET /health` tra `200`, co status, uptime, version va dependencies.
- [x] `GET /ready` tra `200` khi Redis san sang, `503` khi chua san sang.
- [x] `POST /ask` validate JSON va tra `422` neu payload sai.
- [x] `POST /ask` tra `401` khi thieu hoac sai API key.
- [x] `POST /ask` tra `429` khi vuot rate limit.
- [x] `POST /ask` tra `402` khi vuot monthly budget.
- [x] Conversation history duoc luu trong Redis theo `user_id`.
- [x] State chia se duoc giua nhieu worker/instance.

## 4. Checklist container

- [x] Multi-stage `Dockerfile`.
- [x] Runtime dung Python slim.
- [x] Container chay bang non-root user.
- [x] Docker `HEALTHCHECK`.
- [x] `.dockerignore` bo `.env`, cache, virtualenv va Git.
- [x] `docker-compose.yml` co agent + Redis.
- [x] Redis co healthcheck va persistent volume.
- [x] Agent doc `PORT` va cac bien cau hinh tu environment.
- [x] Docker image build thanh cong, kich thuoc `187 MB`.
- [x] Docker Compose stack chay va vuot integration test.

## 5. Checklist kiem thu

- [x] Co unit/integration test cho health, readiness, auth, rate limit,
  cost guard va conversation history.
- [x] `python check_production_ready.py` dat 100% (`22/22`).
- [x] `pytest` pass (`6/6`).
- [x] `docker compose config` pass.
- [x] `docker compose up --build` pass.
- [x] Kiem tra image size `< 500 MB` (`187 MB`).

## 6. Checklist deployment

- [x] Co `railway.toml`.
- [x] Co `render.yaml`.
- [x] Chon Railway.
- [x] Tao Redis service tren cloud.
- [x] Set `ENVIRONMENT=production`.
- [x] Set `AGENT_API_KEY` bang secret manh.
- [x] Sua reference `REDIS_URL` de agent ket noi Redis.
- [x] Deploy web service thanh cong.
- [x] `GET <PUBLIC_URL>/health` tra `200`.
- [x] `GET <PUBLIC_URL>/ready` tra `200`.
- [x] Request khong co key tra `401`.
- [x] Request co key tra `200`.
- [x] Goi qua limit tra `429`.

## 7. Checklist ho so nop bai

- [x] `MISSION_ANSWERS.md` tra loi Part 1-5.
- [x] `DEPLOYMENT.md` co platform, env vars va lenh test.
- [x] Cap nhat public URL that trong `DEPLOYMENT.md`.
- [x] `06-lab-complete/README.md` co huong dan local va deployment.
- [x] `screenshots/dashboard.png`.
- [x] `screenshots/running.png`.
- [x] `screenshots/testing1.png` va `screenshots/testing2.png`.
- [x] Public GitHub repository.
- [x] Khong commit `.env`, API key that hoac Redis credentials trong working
  tree va Git history.
- [x] Da dien Student Name, Student ID va Date.

CI/CD khong bat buoc trong rubric 100 diem. Cloud Run CI/CD la bai optional va
GitHub Actions la next step sau lab.

## 8. Lenh verify cuoi

```powershell
cd 06-lab-complete
python -m pip install -r requirements-dev.txt
python check_production_ready.py
python -m pytest -q
docker compose config
docker compose up --build -d
docker compose ps
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
curl.exe -X POST http://localhost:8000/ask `
  -H "X-API-Key: dev-key-change-me" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":\"demo\",\"question\":\"Hello\"}'
docker compose down
```

## 9. Viec can thao tac tai khoan

Nhung muc sau khong the tu dong hoan tat neu chua dang nhap cloud:

- Tao project Railway/Render va Redis service.
- Gan domain public.
- Them secrets tren dashboard.
- Chup anh dashboard va ket qua public URL.
- Push repository len GitHub.

## 10. Trang thai verify hien tai

- Static production checker: `22/22` pass.
- Python tests: `6/6` pass.
- Python compile: pass.
- Docker Compose config: pass.
- Docker build/runtime: pass; agent va Redis deu healthy.
- Docker image size: `187 MB`.
- Develop image size: about `1.15 GB`; production reduction: `83.7%`.
- Live endpoints: `200`, missing-key `401`, budget `402`, rate limit `429`.
- Conversation history: Redis-backed multi-turn test pass.
- Graceful shutdown: SIGTERM test pass for both Uvicorn workers.
