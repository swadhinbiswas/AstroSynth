# Changelog — AstroSynth

## v1.1.0

**Real data and honest metrics**

- Training now uses 9,201 real KOI rows from the NASA Exoplanet Archive (TAP), fetched by `ml/scripts/download_nasa.py`
- Optuna tuning is wired in: 30 trials per model, 120 runs total
- All four models train on real data: XGBoost 0.782 F1, CatBoost 0.779, LightGBM 0.776, RandomForest 0.769
- `/leaderboard` and `/metrics` read `ml/artifacts/registry.json` instead of holding hardcoded numbers
- `registry.json` records dataset provenance plus `is_synthetic` so generated-fixture runs are never mistaken for real results

**Persistence**

- Predictions, feedback and audit rows now write to PostgreSQL (new `/predictions/stats` endpoint)
- A circuit breaker disables writes for 60 s after the first failure, so running without a database does not slow requests
- The API still serves predictions with no database; it logs the skipped write once

**Explainability**

- SHAP TreeExplainer runs when `shap` is installed; the response labels the method as `shap-tree-explainer` or `permutation-fallback`
- The fallback no longer claims to be SHAP

**Frontend**

- Leaderboard and analytics read live API data; the invented class-balance pie chart is replaced with real served-prediction counts
- Landing stats now report the actual training set size and F1

**Tests**

- Backend grew from 7 to 27 tests, split into API (19) and persistence (8)
- Persistence tests run against a real database and skip themselves cleanly when none is reachable
- Database check constraints (`users.role`, `predictions.confidence`) are now tested

## v1.0.0 (2025-09-30)
- Prediction engine (single + batch) with SHAP explanations
- Mission / dataset explorer (Kepler, K2, TESS)
- Leaderboard (RF, XGB, LGBM, CatBoost) + analytics dashboard
- Research workspace with Markdown export
- JWT + RBAC, rate limiting, audit logging
- Postgres schema + Alembic 0001 + seeds
- Docker Compose (app + db + Prometheus + Grafana), CI/CD
- Full docs: architecture, API, deployment, methodology, model card
