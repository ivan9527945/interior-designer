"""Job dispatcher — Redis LPUSH/RPOP queue；連不上時 fallback 到記憶體 deque。"""

import json
from collections import deque
from typing import Any

import structlog

from app.config import get_settings

log = structlog.get_logger(__name__)

_QUEUE: deque[dict[str, Any]] = deque()
_REDIS_KEY = "rs:job:queue"
_JOB_TTL = 7200


async def _get_redis():
    """取得 Redis 連線；失敗回傳 None。"""
    try:
        import redis.asyncio as aioredis  # noqa: PLC0415

        client = aioredis.from_url(get_settings().REDIS_URL)
        await client.ping()
        return client
    except Exception as e:
        log.warning("job_dispatcher_redis_unavailable", error=str(e))
        return None


async def enqueue(job: dict[str, Any]) -> None:
    redis = await _get_redis()
    if redis is not None:
        try:
            payload = json.dumps(job)
            await redis.lpush(_REDIS_KEY, payload)
            await redis.expire(_REDIS_KEY, _JOB_TTL)
            return
        except Exception as e:
            log.warning("job_dispatcher_redis_enqueue_failed_fallback", error=str(e))

    # fallback: 記憶體 deque
    _QUEUE.append(job)


async def pop() -> dict[str, Any] | None:
    redis = await _get_redis()
    if redis is not None:
        try:
            raw = await redis.rpop(_REDIS_KEY)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            log.warning("job_dispatcher_redis_pop_failed_fallback", error=str(e))

    # fallback: 記憶體 deque
    if not _QUEUE:
        return None
    return _QUEUE.popleft()
