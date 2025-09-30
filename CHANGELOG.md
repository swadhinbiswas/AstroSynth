# Changelog — AstroSynth

## v1.1.0
- Live 3D planet renderer (Three.js): procedural surface, atmosphere, rings, moon — driven in real time by prediction parameters
- Pixel-perfect polish pass: mobile nav, balanced type, tabular numerals, focus rings, reduced-motion support
- Planet telemetry panel: class, radius, temp, insolation + habitable-zone estimate with session clock

## v1.0.0 (2025-09-30)
- Prediction engine (single + batch) with SHAP explanations
- Mission / dataset explorer (Kepler, K2, TESS)
- Leaderboard (RF, XGB, LGBM, CatBoost) + analytics dashboard
- Research workspace with Markdown export
- JWT + RBAC, rate limiting, audit logging
- Postgres schema + Alembic 0001 + seeds
- Docker Compose (app + db + Prometheus + Grafana), CI/CD
- Full docs: architecture, API, deployment, methodology, model card
