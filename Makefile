.PHONY: help bootstrap dev-frontend dev-backend dev-agent dev-worker \
        sync-schema lint test clean

# macOS Celery fork-safety
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY := YES

PY311 := $(shell command -v python3.11 2>/dev/null || echo python3)

help:
	@echo "RenderStudio — Monorepo targets"
	@echo ""
	@echo "  make bootstrap       建立 backend/agent 虛擬環境並安裝依賴"
	@echo "  make dev-frontend    起 Next.js dev server (port 3000)"
	@echo "  make dev-backend     起 FastAPI + uvicorn (port 8000)"
	@echo "  make dev-worker      起 Celery worker (solo pool, macOS)"
	@echo "  make dev-agent       起本機 Agent"
	@echo "  make sync-schema     後端 Pydantic -> shared/style_schema.json"
	@echo "  make lint            三端 lint + type-check"
	@echo "  make test            三端測試"
	@echo "  make clean           清理 __pycache__ / .next / node_modules"

bootstrap:
	pnpm install
	cd backend && $(PY311) -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e '.[dev]'
	cd agent && $(PY311) -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e '.[dev]'

dev-frontend:
	pnpm --filter frontend dev

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-worker:
	cd backend && . .venv/bin/activate && \
		OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
		celery -A app.tasks.celery_app worker --pool=solo --loglevel=info

dev-agent:
	cd agent && . .venv/bin/activate && python -m renderstudio_agent

sync-schema:
	cd backend && . .venv/bin/activate && python scripts/export_style_schema.py > ../shared/style_schema.json
	@echo "✓ shared/style_schema.json updated"

lint:
	pnpm --filter frontend lint
	cd backend && . .venv/bin/activate && ruff check app tests && mypy app
	cd agent && . .venv/bin/activate && ruff check renderstudio_agent tests

test:
	pnpm --filter frontend test
	cd backend && . .venv/bin/activate && pytest
	cd agent && . .venv/bin/activate && pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf frontend/.next frontend/node_modules
	rm -rf backend/.venv agent/.venv
