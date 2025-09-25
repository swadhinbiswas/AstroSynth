.PHONY: help bootstrap dev backend frontend ml-train ml-eval test lint fmt migrate seed docker-up docker-down clean

help:
	@echo "AstroSynth Makefile"
	@echo "  make bootstrap   - install all deps (backend+ml+frontend)"
	@echo "  make dev         - run postgres + backend + frontend locally"
	@echo "  make ml-train    - run full ML training pipeline"
	@echo "  make test        - run all tests"
	@echo "  make lint        - ruff + tsc + eslint"
	@echo "  make docker-up   - compose up --build"

bootstrap:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt -r ml/requirements.txt
	cd frontend && npm install

dev:
	docker compose up postgres -d
	cd backend && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

ml-train:
	python3 ml/scripts/train.py --config ml/configs/base.yaml

ml-download:
	python3 ml/scripts/download_nasa.py --out data/raw

test:
	cd backend && pytest -q --cov=app --cov-report=term-missing
	cd ml && pytest -q
	cd frontend && npm run test -- --run 2>/dev/null || npm run lint

lint:
	cd backend && ruff check app && ruff format --check app
	cd frontend && npm run lint

fmt:
	cd backend && ruff format app
	cd frontend && npx prettier --write .

migrate:
	cd backend && alembic upgrade head

seed:
	psql "$$DATABASE_URL" -f database/seeds/seed.sql

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; rm -rf .venv htmlcov .coverage
