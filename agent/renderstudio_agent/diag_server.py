"""本機診斷 HTTP server — http://localhost:9787/diag"""

import asyncio
import json
import platform
from datetime import UTC, datetime

import structlog

from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)

AGENT_VERSION = "0.1.0"

try:
    import psutil as _psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def _get_system_info() -> dict | None:
    """回傳 CPU / 記憶體 / 磁碟使用資訊；若 psutil 未安裝則回 None。"""
    if not _HAS_PSUTIL:
        return None
    try:
        disk = _psutil.disk_usage("/")
        return {
            "cpu_percent": _psutil.cpu_percent(interval=0.1),
            "memory_percent": _psutil.virtual_memory().percent,
            "disk_free_gb": round(disk.free / (1024 ** 3), 1),
        }
    except Exception:
        return None


def _build_diag_body() -> str:
    settings = get_settings()
    mac_ver = platform.mac_ver()[0] or "unknown"
    machine = platform.machine()

    body = {
        "ok": True,
        "time": datetime.now(UTC).isoformat(),
        "agent_version": AGENT_VERSION,
        "platform": f"macOS {mac_ver} {machine}",
        "python_version": platform.python_version(),
        "settings": {
            "api_base": settings.RS_API_BASE,
            "vray_version": settings.VRAY_VERSION,
            "diag_port": settings.DIAG_PORT,
        },
        "system": _get_system_info(),
    }
    return json.dumps(body)


def _http_response(status: str, content_type: str, body: str) -> bytes:
    return (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        + body
    ).encode()


async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        raw = await reader.readuntil(b"\r\n\r\n")
    except asyncio.IncompleteReadError:
        writer.close()
        return

    # 解析請求行，取得 path
    first_line = raw.split(b"\r\n")[0].decode(errors="replace")
    parts = first_line.split(" ")
    path = parts[1] if len(parts) >= 2 else "/"

    if path == "/diag":
        body = _build_diag_body()
        response = _http_response("200 OK", "application/json", body)
    elif path == "/health":
        body = json.dumps({"ok": True})
        response = _http_response("200 OK", "application/json", body)
    else:
        body = json.dumps({"ok": False, "error": "not found"})
        response = _http_response("404 Not Found", "application/json", body)

    writer.write(response)
    await writer.drain()
    writer.close()


async def start_diag_server() -> asyncio.AbstractServer:
    settings = get_settings()
    server = await asyncio.start_server(_handle, "127.0.0.1", settings.DIAG_PORT)
    log.info("diag_server_started", port=settings.DIAG_PORT)
    return server
