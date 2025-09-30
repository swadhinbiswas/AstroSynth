# Deployment Guide

## Local

```bash
cp .env.example .env
docker compose up --build
```

Ports: frontend 3000, backend 8000, postgres 5432, prometheus 9090, grafana 3001.

Postgres is optional. Without it the API still serves predictions; writes to `predictions`,
`feedback` and `audit_logs` are skipped and logged once, then suppressed for 60 seconds.

## Training before serving

The API runs with a startup fallback model, which exists so the UI works on a fresh clone. Do
not ship that. Train a real model first:

```bash
pip install -r ml/requirements.txt
python ml/scripts/download_nasa.py --out data/raw
python ml/scripts/train.py --config ml/configs/base.yaml --input data/raw/koi_train.csv
```

That writes `ml/artifacts/model_*.joblib` and `ml/artifacts/registry.json`. The API reads both:
the joblib files for inference, the registry for every metric it reports.

Expected runtime: the download takes under a minute, training takes several minutes depending
on `optuna_trials`. Set it to 0 in `ml/configs/base.yaml` to skip tuning.

## Production checklist

1. Set a strong `JWT_SECRET` (32+ characters), a real `POSTGRES_PASSWORD`, and a Grafana admin password. Treat all three as secrets.
2. Use managed Postgres. Set `DATABASE_URL`, then run `alembic upgrade head` before starting the API.
3. Train and bake the artifacts. Either copy `ml/artifacts/` into the backend image or mount it read-only at `/app/ml_artifacts`.
4. Terminate TLS in front of the backend (Caddy or Nginx) and set `CORS_ORIGINS` to your frontend domain. The current default allows `*`, which is fine for a demo and wrong for anything public.
5. Run `docker compose -f docker-compose.prod.yml` for the reduced stack. It drops the monitoring services.
6. Add a `GHCR_TOKEN` secret if you want the CD workflow to push images. It currently only builds.

## Health gates

- `GET /api/v1/health` returns `{"status":"ok","model_loaded":true}`. If `model_loaded` is false, no artifact and no fallback could be constructed; check the logs.
- `GET /api/v1/leaderboard` should report `trained: true`. If it reports `false`, the registry is missing and the UI will show an empty table.
- `GET /metrics-prom` is scraped by Prometheus. The dashboard definition lives in `infra/grafana/dashboards/`.

## Known gaps before this is production-grade

These are deliberate scope choices, not oversights. Each one is a real risk if you deploy publicly:

| Gap | Risk | Fix |
|---|---|---|
| In-memory rate limiter | Resets on restart, and does not work across replicas | Move to Redis |
| Fallback model at startup | Serves meaningless predictions silently | Fail fast when no artifact is present |
| `POST /predict` is unauthenticated | Anyone can call it, bounded only by the rate limit | Require a bearer token |
| Demo auth stores users in memory | Registered accounts vanish on restart | Back `/auth/register` with the `users` table |
| No request-size cap at the proxy | A large batch body is parsed before the 1000-row check | Add a body limit in Caddy or Nginx |
