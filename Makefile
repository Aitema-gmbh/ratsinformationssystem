# aitema|Rats - Makefile

.PHONY: dev build test lint clean

dev:
	docker compose up --build

dev-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

build:
	docker compose build

test:
	cd backend && python -m pytest tests/ -v

test-oparl:
	cd backend && python -m pytest tests/test_oparl.py -v

lint:
	cd backend && ruff check . && mypy app/
	cd frontend && npm run lint

db-migrate:
	cd backend && alembic upgrade head

db-seed:
	cd backend && python -m app.seeds.demo_data

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/.next frontend/node_modules
