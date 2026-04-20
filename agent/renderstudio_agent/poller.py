"""Long-poll 取任務。"""

from typing import Any

import structlog

from renderstudio_agent.api_client import ApiClient

log = structlog.get_logger(__name__)


async def poll_next_job(client: ApiClient) -> dict[str, Any] | None:
    try:
        return await client.next_job()
    except Exception as e:
        log.warning("poll_failed", error=str(e))
        return None
