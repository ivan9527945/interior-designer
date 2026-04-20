"""SSE 事件 broker — 從 Agent 進度回報 fan-out 到訂閱瀏覽器。

骨架版：每個 renderId 一個 asyncio.Queue。
正式版：Redis Pub/Sub，多 API replica 共享。
"""

import asyncio
from collections import defaultdict
from typing import Any

_subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)


def subscribe(render_id: str) -> asyncio.Queue[dict[str, Any]]:
    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    _subscribers[render_id].append(q)
    return q


def unsubscribe(render_id: str, q: asyncio.Queue[dict[str, Any]]) -> None:
    if q in _subscribers.get(render_id, []):
        _subscribers[render_id].remove(q)


async def publish(render_id: str, event: dict[str, Any]) -> None:
    for q in _subscribers.get(render_id, []):
        await q.put(event)
