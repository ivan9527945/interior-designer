"""SSE endpoint — 推渲染進度給瀏覽器。"""

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.services.sse_broker import subscribe, unsubscribe

router = APIRouter(tags=["stream"])


@router.get("/renders/{render_id}/stream")
async def stream_render(render_id: str):
    settings = get_settings()
    queue = subscribe(render_id)

    async def event_gen() -> AsyncIterator[dict]:
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=settings.SSE_KEEPALIVE_SECONDS)
                    yield {"event": event.get("event", "progress"), "data": json.dumps(event.get("data", {}))}
                except asyncio.TimeoutError:
                    # Keepalive comment
                    yield {"event": "ping", "data": ""}
        finally:
            unsubscribe(render_id, queue)

    return EventSourceResponse(event_gen())
