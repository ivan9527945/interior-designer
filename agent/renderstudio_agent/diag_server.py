"""本機診斷 HTTP server — http://localhost:9787/diag"""

import asyncio
import json
from datetime import UTC, datetime

import structlog

from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)


async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        await reader.readuntil(b"\r\n\r\n")
    except asyncio.IncompleteReadError:
        writer.close()
        return

    body = json.dumps(
        {
            "ok": True,
            "time": datetime.now(UTC).isoformat(),
            "agent_version": "0.1.0",
        }
    )
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n" + body
    )
    writer.write(response.encode())
    await writer.drain()
    writer.close()


async def start_diag_server() -> asyncio.AbstractServer:
    settings = get_settings()
    server = await asyncio.start_server(_handle, "127.0.0.1", settings.DIAG_PORT)
    log.info("diag_server_started", port=settings.DIAG_PORT)
    return server
