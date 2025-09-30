# AstroSynth Architecture

## Topology

```
Browser (Next.js 15, dark space theme)
  │  REST /api/v1 (TanStack Query + Zustand)
  ▼
FastAPI (uvicorn)
  │  ├─ services/predictor.py    joblib artifact, or a startup fallback when none exists
  │  ├─ services/shap_service.py TreeExplainer, or permutation values labelled as such
  │  ├─ services/registry.py     reads ml/artifacts/registry.json for all reported metrics
  │  ├─ services/telemetry.py    writes predictions, feedback, audit rows; circuit-broken
  │  ├─ services/catalog.py      static mission and dataset catalogue
  │  └─ /metrics-prom            Prometheus scrapes this
  ▼
PostgreSQL 16 (users, datasets, models, predictions, experiments, reports, feedback, audit_logs)
  │
ML offline: ml/scripts/download_nasa.py → ml/scripts/train.py → ml/artifacts/{model_*.joblib, registry.json}
```

Postgres is optional at runtime. Every persistence call goes through `telemetry.py`, which
trips a breaker after the first failure and stops retrying for 60 seconds. A demo without a
database answers as fast as one with it.

## Request flow: POST /predict

1. `ExoplanetFeatures` validates ten fields against physical bounds. `extra="forbid"`, so a
   misspelled column returns 422 instead of being silently ignored.
2. Rate limit check, 60/min/IP. The audit middleware records the call.
3. `predict_proba` expands the ten inputs to the fourteen features the model was trained on,
   then returns a class, a confidence, and the full probability distribution.
4. `explain_local` returns SHAP values. If `shap` is not installed, it returns permutation
   attributions and sets `method` to `permutation-fallback`.
5. The prediction is written to Postgres, unless the breaker is open.
6. Response: `{predicted_class, confidence, probabilities, explanations, model_name, model_version}`.

## Where the numbers come from

Every metric the UI displays is read from `ml/artifacts/registry.json` at request time. There is
no second copy to drift. If the file is absent, `/leaderboard` returns `trained: false` and an
empty list rather than placeholder scores.

`registry.json` also records `dataset.is_synthetic`. Training on the generated fixture produces
near-perfect scores by construction, because the labels are a fixed rule over two columns. That
flag exists so those runs are never mistaken for real results.

## Why this shape

- **Serving a frozen artifact** keeps a prediction reproducible, at 0.6 s measured end to end
  including the database write.
- **Explainability is a response field**, not a separate endpoint, so a caller cannot get a
  verdict without also getting the reason.
- **The schema exists twice on purpose.** `database/schema.sql` is readable SQL for review;
  `backend/alembic/versions/0001_initial.py` is the migration that actually runs. Tests assert
  the constraints hold, so the two cannot silently diverge.
- **Train and serve share feature logic**, mirrored in `ml/src/features.py` and
  `backend/app/services/predictor.py`. A test fails if a served explanation is missing any
  contract feature.

## Scaling path

- In-memory rate limit to Redis, so it survives restarts and works across replicas.
- Local joblib artifacts to S3 plus MLflow Model Registry.
- Snapshot training data to live TAP queries with a cache in front.
- Synchronous batch predict to a job queue with polling.
- Single Postgres to read replicas, with `predictions` partitioned by month.
