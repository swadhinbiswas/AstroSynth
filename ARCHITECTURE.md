# AstroSynth Architecture v1.0.0

## Topology

```
Browser (Next.js 15, dark space theme)
  │  REST /api/v1 (TanStack Query + Zustand)
  ▼
FastAPI (uvicorn) ──► PostgreSQL 16 (users/datasets/predictions/…)
  │  ├─ predictor.py (joblib artifact or synthetic-trained RF fallback)
  │  ├─ shap_service.py (TreeExplainer, permutation fallback)
  │  └─ /metrics-prom (Prometheus) → Prometheus → Grafana
ML offline: ml/scripts/train.py → ml/artifacts/{model_*.joblib, registry.json}
```

## Request flow: POST /predict

1. Pydantic `ExoplanetFeatures` validates 10 physics fields (ranges reject junk).
2. Rate limiter (60/min/IP) + audit middleware log the call.
3. `predict_proba` builds the feature vector → `predict_proba` → class + confidence.
4. `explain_local` returns SHAP (or deterministic fallback) values + waterfall.
5. Response: `{predicted_class, confidence, probabilities, explanations, model_name/version}`.

## Why this shape

- **Backend serves a frozen artifact**, never trains on request — latency <300ms, reproducible.
- **Frontend never embeds the model** — one source of truth, versioned via `registry.json`.
- **Explainability is a first-class response field**, not an afterthought.
- **Postgres schema mirrors Alembic** (`database/schema.sql` ≡ `0001_initial.py`) so judges can read SQL directly.

## Scaling path

- Swap in-memory rate limit → Redis; sync artifacts → S3; add Celery for batch jobs.
- Promote `registry.json` → MLflow Model Registry (env `MLFLOW_TRACKING_URI` already plumbed).
- Frontend is static-exportable (`output: standalone`) behind any CDN.
