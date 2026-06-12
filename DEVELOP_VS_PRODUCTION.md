# Develop vs Production Analysis

Tai lieu nay tong hop ket qua doi chieu source code thuc te cua cac module
`01` den `05`. Phan "production" duoc danh gia theo ca y tuong kien truc va
muc do co the chay ngay, khong chi dua tren mo ta trong README.

## Tong quan

| Module | Develop | Production |
|---|---|---|
| 01 | Local, hardcode config | 12-factor, health checks, logging |
| 02 | Docker single-stage | Multi-stage, non-root, Compose, Nginx |
| 03 | Railway/Render | Cloud Run va CI/CD |
| 04 | API key | JWT, role, rate limit, cost guard |
| 05 | Health va shutdown | Redis stateless, multi-instance, load balancing |

## 01 - Localhost vs Production

### Develop

- Hardcode OpenAI key va database credentials trong source.
- Bind server vao `localhost`.
- Port `8000` va debug reload duoc bat co dinh.
- Dung `print()` thay vi structured logging.
- Log ca API key.
- Khong co health check, readiness hay metrics.

### Production

- Doc config va secrets tu environment variables.
- Bind `0.0.0.0`, doc port tu `PORT`.
- Co `GET /health`, `GET /ready` va `GET /metrics`.
- Co structured JSON logging va CORS configuration.
- Quan ly startup/shutdown qua FastAPI lifespan.
- Validate `AGENT_API_KEY` khi chay trong production.

### Han che

`AGENT_API_KEY` duoc validate trong config nhung endpoint `/ask` chua thuc su
kiem tra authentication.

## 02 - Docker

### Develop

- Dockerfile single-stage.
- Dung image `python:3.11` day du, kich thuoc lon.
- Container chay bang root.
- Mot agent process don gian.
- Chi co health endpoint co ban.

### Production

- Dockerfile multi-stage voi `python:3.11-slim`.
- Tao va chay bang non-root user.
- Co Docker `HEALTHCHECK`.
- Chay nhieu Uvicorn workers.
- Co readiness, lifespan va structured logging.
- Docker Compose khai bao agent, Redis, Qdrant va Nginx.
- Nginx lam reverse proxy, load balancer va rate limiter.

### Bat nhat va loi

- Thieu `02-docker/production/requirements.txt`.
- Compose yeu cau `.env.local` nhung file khong ton tai.
- Build context cua Compose khong khop cac duong dan `COPY` trong Dockerfile.
- Redis va Qdrant duoc khoi dong nhung `main.py` chua su dung.
- Cach copy package `--user` sang non-root home co nguy co lam Python khong tim
  thay dependencies.

## 03 - Cloud Deployment

Module nay khong co cap thu muc `develop/production`. No chia theo muc do phuc
tap cua platform.

### Railway

- Cau hinh don gian bang `railway.toml`.
- Nixpacks tu dong build.
- Co start command, health check va restart policy.
- Co san `app.py` va `requirements.txt`.

### Render

- Infrastructure-as-code bang `render.yaml`.
- Khai bao web service va Redis.
- Tu dong sinh `AGENT_API_KEY`.
- Auto deploy khi GitHub thay doi.

### Cloud Run

- Autoscaling tu 1 den 10 instances.
- Cau hinh CPU, memory, concurrency va timeout.
- Doc secrets tu Secret Manager.
- Co liveness va startup probes.
- Cloud Build chay test, build image, push va deploy tu dong.

### Bat nhat va loi

- Thu muc Render thieu `app.py` va `requirements.txt`, cung khong khai bao
  `rootDir`.
- Thu muc Cloud Run thieu Dockerfile, requirements va tests tuong ung.
- `service.yaml` con placeholder `PROJECT_ID`.
- Cloud Build deploy chi set `OPENAI_API_KEY`, thieu `AGENT_API_KEY`.

Railway la vi du co kha nang chay doc lap tot nhat trong module `03`.

## 04 - API Gateway

### Develop

- Xac thuc bang header `X-API-Key`.
- Thieu hoac sai key tra `401`.
- API key doc tu environment.
- Khong co role, rate limit hay budget protection.

### Production

- Login bang username/password de nhan JWT.
- Bearer token co thoi han 60 phut.
- Co role `user` va `admin`.
- User gioi han 10 request/phut, admin 100 request/phut.
- Co cost guard theo user va global.
- Co Pydantic input validation.
- Them security headers.
- Co endpoint xem usage va admin stats.

### Han che

- Demo username/password van hardcode.
- `JWT_SECRET` co default khong an toan.
- Rate limit va cost usage luu trong RAM.
- Restart se mat du lieu.
- Nhieu worker se co quota rieng.

Vi vay day la demo security nang cao, chua phai implementation production hoan
chinh.

## 05 - Scaling and Reliability

### Develop

- Co liveness va readiness endpoints.
- Health endpoint kiem tra uptime va memory.
- Theo doi so request dang xu ly.
- Graceful shutdown cho toi da 30 giay de hoan tat request.
- Chi chay mot instance.
- Khong co conversation history dung chung.

### Production

- Luu session va conversation history trong Redis.
- Session co TTL va gioi han toi da 20 messages.
- Ho tro nhieu agent instances.
- Nginx phan phoi request giua cac instance.
- Response cho biet instance nao da xu ly.
- Co script kiem tra history van ton tai khi request doi instance.

### Bat nhat va loi

- Compose tro toi `05-scaling-reliability/advanced/Dockerfile`, nhung thu muc
  `advanced` khong ton tai.
- Thu muc production khong co Dockerfile.
- Compose yeu cau `.env.local` nhung file khong ton tai.
- Khi Redis loi, app fallback ve RAM va khong con stateless.
- Production van chay `reload=True`.
- Mock LLM khong thuc su dung conversation history de tao cau tra loi.

## Ket luan

Các thu muc production the hien dung huong kien truc, nhung khong phai tat ca
deu chay duoc ngay:

- `01`: gan hoan chinh, nhung chua ap dung auth vao endpoint.
- `02`: kien truc container tot, nhung build configuration con loi.
- `03`: Railway hoan thien nhat; Render va Cloud Run thieu artifact.
- `04`: nhieu lop security hon, nhung state van la in-memory demo.
- `05`: y tuong stateless dung, nhung Compose hien khong build duoc.

Project `06-lab-complete` da khac phuc phan lon cac diem tren bang API key auth,
Redis-backed state, rate limiting, cost guard, multi-stage Docker image, non-root
runtime, multi-worker va integration tests.
