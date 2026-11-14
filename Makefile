.PHONY: dev-api dev-worker dev-web test build up down

dev-api:
	cd backend && uv run --extra dev uvicorn app.main:app --reload

dev-worker:
	cd backend && uv run python -m app.worker

dev-web:
	cd frontend && npm run dev

test:
	cd backend && uv run --extra dev pytest -q

build:
	cd frontend && npm run build

up:
	docker compose up --build

down:
	docker compose down

