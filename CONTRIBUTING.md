# Contributing — AstroSynth

## Commits (Conventional Commits, enforced in review)

`feat:`, `fix:`, `docs:`, `ml:`, `refactor:`, `test:`, `chore:`, `ci:` — e.g. `ml: add catboost + optuna tuning`.

Original build timeline (Sept 2025 recreation):
- 2025-09-25 scaffold + DB schema
- 2025-09-26 backend API + auth
- 2025-09-27 ML pipeline + tuning
- 2025-09-28 frontend + visualizations
- 2025-09-29 explainability + workspace
- 2025-09-30 docs + hardening + release v1.0.0

## PR rules

1. `ruff check` + `pytest` green (backend + ml); `npm run lint && npm run build` green (frontend).
2. New endpoints need OpenAPI-tested tests in `backend/tests/`.
3. New features need a docs line in `README.md` or `docs/`.
4. Never commit `.env`, artifacts (`*.joblib`), or `data/`.
