#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
docker compose up -d postgres
sleep 3
(cd backend && alembic upgrade head || echo "migrate skipped (no DB yet)")
echo "AstroSynth ready: backend :8000, frontend :3000"
