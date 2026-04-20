import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import agents, auth, projects, renders, share, spaces, stream, style, uploads

settings = get_settings()

logging.basicConfig(level=settings.LOG_LEVEL)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

app = FastAPI(
    title="RenderStudio API",
    version="0.1.0",
    description="Web + 本機 Agent 室內渲染平台",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(spaces.router)
app.include_router(uploads.router)
app.include_router(style.router)
app.include_router(renders.router)
app.include_router(agents.router)
app.include_router(stream.router)
app.include_router(share.router)


@app.get("/healthz", tags=["system"])
async def healthz():
    return {"status": "ok", "version": app.version}
