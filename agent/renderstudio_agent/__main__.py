"""Agent entry — 骨架版只跑 poll loop，不真的 execute job。"""

import asyncio
import platform

import structlog

from renderstudio_agent.api_client import ApiClient
from renderstudio_agent.config import get_settings
from renderstudio_agent.diag_server import start_diag_server
from renderstudio_agent.heartbeat import heartbeat_loop
from renderstudio_agent.poller import poll_next_job
from renderstudio_agent.utils import configure_logging

log = structlog.get_logger(__name__)


async def register_or_resume(client: ApiClient) -> str:
    """Sprint 1 骨架：回 stub agent_id。"""
    # TODO (Sprint 2): 真的呼叫 /agent/register，儲存 token
    settings = get_settings()
    _ = platform.mac_ver()
    log.info(
        "agent_starting",
        api_base=settings.RS_API_BASE,
        sketchup=settings.SKETCHUP_APP,
    )
    return "stub-agent-id"


async def execute_job(job: dict) -> None:
    # TODO (Sprint 2): 真的執行 DXF 解析 → SketchUp → V-Ray
    log.info("job_received_stub", job_id=job.get("id", "unknown"))


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    client = ApiClient()
    agent_id = await register_or_resume(client)

    # Diag server + heartbeat 並行跑
    diag_server = await start_diag_server()
    heartbeat_task = asyncio.create_task(heartbeat_loop(client, agent_id))

    try:
        while True:
            log.info("polling")
            try:
                job = await poll_next_job(client)
                if job:
                    await execute_job(job)
            except Exception as e:
                log.exception("main_loop_error", error=str(e))
            await asyncio.sleep(5)
    finally:
        heartbeat_task.cancel()
        diag_server.close()
        await diag_server.wait_closed()
        await client.close()


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
