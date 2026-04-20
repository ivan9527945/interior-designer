"""Job dispatcher — 進 Redis queue 等 Agent 拉任務。骨架版用記憶體 deque。"""

from collections import deque
from typing import Any

_QUEUE: deque[dict[str, Any]] = deque()


async def enqueue(job: dict[str, Any]) -> None:
    # TODO (Sprint 2): 用 Redis LPUSH + Celery
    _QUEUE.append(job)


async def pop() -> dict[str, Any] | None:
    if not _QUEUE:
        return None
    return _QUEUE.popleft()
