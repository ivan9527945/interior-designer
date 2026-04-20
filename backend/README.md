# RenderStudio Backend

FastAPI + SQLAlchemy + Celery + Redis + MinIO + Anthropic.

## Dev

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/healthz

## Celery worker (macOS)

```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A app.tasks.celery_app worker --pool=solo
```

## Sync shared schema

```bash
python scripts/export_style_schema.py > ../shared/style_schema.json
```
