"""每 5 秒回報心跳。"""

import asyncio

import structlog

from renderstudio_agent.api_client import ApiClient
from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)


async def heartbeat_loop(client: ApiClient, agent_id: str) -> None:
    settings = get_settings()
    while True:
        try:
            await client.heartbeat({"agentId": agent_id, "cpu": 0.0})
        except Exception as e:
            log.warning("heartbeat_failed", error=str(e))
        await asyncio.sleep(settings.HEARTBEAT_INTERVAL_SECONDS)
