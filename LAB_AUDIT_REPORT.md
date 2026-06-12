# Day 12 Lab - Final Audit Report

**Student Name:** Trần Văn Khoa

**Student ID:** 2A202600827

**Audit Date:** 12/06/2026

## Ket luan

Lab da hoan thanh cac yeu cau cham diem bat buoc. Source va kiem thu local dat
100%, web service Railway co public URL, Redis da ket noi, `/health` va `/ready`
tra `200`, authenticated `/ask` tra `200`, va public rate limit tra `429` sau
10 request. Repository GitHub public va cac screenshot deployment/test da duoc
commit.

CI/CD khong nam trong rubric 100 diem cua Part 6. Trong `CODE_LAB.md`, Cloud Run
CI/CD la Exercise 3.3 optional va GitHub Actions nam trong muc Next Steps. Vi
vay khong can lam them CI/CD de hoan thanh lab nay.

## 1. Source code

Trang thai: **Dat**

- FastAPI agent hoat dong.
- Config doc tu environment variables.
- API key authentication tra `401` khi thieu hoac sai key.
- Redis luu conversation history, rate-limit window va monthly usage.
- Rate limit mac dinh 10 request/phut.
- Cost guard mac dinh 10 USD/thang.
- `/health`, `/ready`, `/ask`, `/usage/{user_id}` va `/metrics`.
- Structured JSON logging va graceful shutdown.
- Khong co production secret that trong source.

## 2. Docker

Trang thai: **Dat**

- Multi-stage Dockerfile.
- Python slim runtime.
- Non-root user.
- Docker healthcheck.
- Agent va Redis deu healthy khi chay Compose.
- Image develop: khoang `1.15 GB`.
- Image final: `187 MB`, nho hon muc `500 MB`.
- Multi-stage/slim image giam khoang `83.7%`.
- SIGTERM/graceful shutdown da verify cho hai Uvicorn workers.

## 3. Tests

Trang thai: **Dat**

- Production readiness checker: `22/22`.
- Pytest: `6/6`, gom health, readiness success/failure, auth, validation,
  history, rate limit va budget.
- Docker integration:
  - `/health`: `200`
  - `/ready`: `200`
  - missing/invalid key: `401`
  - valid request: `200`
  - budget exceeded: `402`
  - rate limit exceeded: `429`
  - invalid payload: `422`

## 4. Reports

Trang thai: **Dat**

- `MISSION_ANSWERS.md`: da co cau tra loi Part 1-5 va ket qua local.
- `DEVELOP_VS_PRODUCTION.md`: da phan tich module 01-05.
- `DEPLOYMENT.md`: da co bien moi truong va lenh deploy/test.
- `docs.md`: checklist cong viec va trang thai.
- `06-lab-complete/README.md`: huong dan local, test va deployment.

- `DAY12_DELIVERY_CHECKLIST.md`: co GitHub repository URL va public URL.
- `screenshots/dashboard.png`: Railway project va Redis online.
- `screenshots/running.png`: deployment active va successful.
- `screenshots/testing1.png`: public `/health` va `/ready`.
- `screenshots/testing2.png`: authenticated `/ask` va public rate limit `429`.

## 5. Repository layout

Rubric mong source final nam tai root repository:

```text
app/
Dockerfile
docker-compose.yml
MISSION_ANSWERS.md
DEPLOYMENT.md
README.md
```

Repository hien tai la repository bai hoc, nen source final nam trong
`06-lab-complete/`.

Khuyen nghi khi nop:

1. Tao repository submission rieng.
2. Dua noi dung `06-lab-complete/` vao root repository moi.
3. Them `MISSION_ANSWERS.md`, `DEVELOP_VS_PRODUCTION.md`, `DEPLOYMENT.md` va
   `screenshots/` vao root repository do.
4. Chay lai checker, pytest va Docker Compose tai root repository moi.

Neu nop ca repository Day 12 hien tai, can noi ro final project nam trong
`06-lab-complete` va yeu cau grader dung folder do lam project root.

## 6. Bat buoc hoan thanh tren cloud

- [x] Chon Railway.
- [x] Tao managed Redis.
- [x] Set `ENVIRONMENT=production`.
- [x] Set secret `AGENT_API_KEY`.
- [x] Set `REDIS_URL`.
- [x] Set `LOG_LEVEL=INFO`.
- [x] Deploy va lay public URL.
- [x] Test `/health`, `/ready` va missing-key auth qua public URL.
- [x] Test valid-key `/ask` qua public URL.
- [x] Test rate limit qua public URL.
- [x] Chup dashboard, deployment status va public endpoint tests.
- [x] Cap nhat `DEPLOYMENT.md`.

## 7. Truoc khi nop

- [x] Dien Student Name, Student ID va Date.
- [x] Kiem tra repository public.
- [x] Kiem tra Git history: khong thay `.env`, Redis credential hay private key;
  cac gia tri giong API key chi nam trong file example/tai lieu mau.
- [x] Xac nhan khong commit `.env`.
- [x] Test public URL qua Railway domain.
- [x] GitHub repository URL da co trong delivery checklist.
