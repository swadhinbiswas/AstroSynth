# Deployment Guide

## Local (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Ports: frontend 3000 · backend 8000 · postgres 5432 · prometheus 9090 · grafana 3001.

## Production checklist

1. Set strong `JWT_SECRET` (≥32 chars), `POSTGRES_PASSWORD`, Grafana password.
2. Use managed Postgres; set `DATABASE_URL`; run `alembic upgrade head`.
3. Bake ML artifacts: `python ml/scripts/train.py` then `COPY ml/artifacts` into backend image (or mount S3).
4. Put backend behind TLS (Caddy/Nginx), restrict `CORS_ORIGINS` to the frontend domain.
5. `docker compose -f docker-compose.yml` + Grafana admin password from secrets manager.
6. Wire CI secret `GHCR_TOKEN` for image pushes (see `.github/workflows/cd.yml`).

## Health gates

- `GET /api/v1/health` → `{"status":"ok","model_loaded":true}`
- `GET /metrics-prom` scraped by Prometheus; dashboard JSON in `infra/grafana/dashboards/`.
