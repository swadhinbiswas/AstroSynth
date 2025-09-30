# ✦ AstroSynth — AI Exoplanet Discovery Platform

**NASA Space Apps Challenge 2025 · “A World Away: Hunting for Exoplanets with AI”**
MIT License · Author: Swadhin Biswas · Project: Sept 25 – Sept 30, 2025 (recreated here as a clean production build)

Classify Kepler / K2 / TESS observations into **Confirmed · Candidate · False Positive** with explainable AI, served through a NASA-grade web platform.

![stack](https://img.shields.io/badge/Next.js-15-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![ML](https://img.shields.io/badge/XGBoost%20%7C%20LightGBM%20%7C%20CatBoost-blue) ![Docker](https://img.shields.io/badge/docker-compose-blue)

## Quickstart (2 minutes)

```bash
cp .env.example .env
docker compose up --build
# frontend http://localhost:3000 · API http://localhost:8000/docs · metrics http://localhost:8000/api/v1/health
```

Without Docker:

```bash
# backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload
# frontend
cd frontend && npm install && npm run dev
# train models (synthetic fallback works offline)
python ml/scripts/train.py --config ml/configs/base.yaml
```

Demo login: `demo@astrosynth.space / demo1234` · Try: **Prediction Studio → Classify**.

## Monorepo layout

```
AstroSynth/
  frontend/   Next.js 15 + Tailwind + live 3D planet (Three.js/R3F) + Recharts + Framer Motion + TanStack Query + Zustand
  backend/    FastAPI + Pydantic v2 + SQLAlchemy + Alembic + JWT/RBAC + Prometheus
  ml/         ingestion → validation → cleaning → features → train → evaluate → explain → registry
  database/   schema.sql · ER diagram (Mermaid) · seeds · mirrors Alembic 0001
  infra/      Prometheus + Grafana provisioning
  .github/    CI (pytest/ruff/next build) + CD (docker build)
  docs/       architecture · API · deployment · methodology · model card
```

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Liveness + model flag |
| GET | `/api/v1/missions` | Kepler / K2 / TESS |
| GET | `/api/v1/datasets` | Dataset index |
| POST | `/api/v1/predict` | Single classification + SHAP |
| POST | `/api/v1/batch-predict` | Up to 1000 rows |
| GET | `/api/v1/model-info` | Active model + importance |
| GET | `/api/v1/leaderboard` | RF vs XGB vs LGBM vs CatBoost |
| GET | `/api/v1/metrics` | Active-model summary |
| POST | `/api/v1/feedback` | Correction labels |

Full reference: `docs/API.md` + live OpenAPI at `/docs`.

## ML pipeline

`download_nasa.py → features.py → train.py → evaluate.py → explain.py → registry.json`

- 10 base + 4 derived physics features (`snr_per_depth`, `log_period`, `radius_ratio`, `temp_ratio`)
- Median imputation, bound-clipping, stratified split, class-balanced learners
- Optuna-ready configs in `ml/configs/`; metrics + artifacts in `ml/artifacts/registry.json`

## Security

JWT (HS256) + RBAC (`admin`/`scientist`/`viewer`), Pydantic strict validation, per-IP rate limiting, audit-log middleware, secure upload size caps (1000 rows/batch), CORS allowlist.

## Docs

- `ARCHITECTURE.md` — system design + request flows
- `docs/API.md` — endpoint contracts + examples
- `DEPLOYMENT.md` — Docker / prod checklist
- `RESEARCH_METHODOLOGY.md` — science rationale
- `MODEL_CARD.md` — intended use, metrics, limits
- `CONTRIBUTING.md` — conventional commits, PR rules
