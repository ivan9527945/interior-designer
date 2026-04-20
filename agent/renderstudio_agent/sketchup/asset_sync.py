"""啟動時從 MinIO pull 材質庫到本地快取目錄。"""

from __future__ import annotations

import os
from pathlib import Path

import aiohttp
import structlog

log = structlog.get_logger(__name__)


async def sync_materials() -> None:
    """從後端 API 拉取材質清單並下載到本地快取目錄。"""
    api_base = os.environ.get("RS_API_BASE", "http://localhost:8000").rstrip("/")
    token = os.environ.get("RS_AGENT_TOKEN", "")

    cache_dir = Path.home() / "Library" / "Application Support" / "RenderStudio" / "materials"
    cache_dir.mkdir(parents=True, exist_ok=True)

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    log.info("sync_materials_start", api_base=api_base, cache_dir=str(cache_dir))

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"{api_base}/materials/list") as resp:
                if resp.status == 404:
                    log.warning("sync_materials_endpoint_not_found", url=f"{api_base}/materials/list")
                    return
                if not resp.ok:
                    log.warning(
                        "sync_materials_api_error",
                        status=resp.status,
                        url=f"{api_base}/materials/list",
                    )
                    return

                data = await resp.json()

    except aiohttp.ClientConnectorError as e:
        log.warning("sync_materials_connection_failed", error=str(e))
        return
    except aiohttp.ClientError as e:
        log.warning("sync_materials_request_failed", error=str(e))
        return

    files: list[dict] = data.get("files", [])
    if not files:
        log.info("sync_materials_no_files")
        return

    log.info("sync_materials_downloading", count=len(files))

    async with aiohttp.ClientSession() as dl_session:
        for item in files:
            key: str = item.get("key", "")
            url: str = item.get("url", "")
            filename: str = item.get("filename", "")

            if not url or not filename:
                log.warning("sync_materials_invalid_entry", key=key)
                continue

            dest = cache_dir / filename
            if dest.exists():
                log.debug("sync_materials_file_exists", filename=filename)
                continue

            try:
                async with dl_session.get(url) as dl_resp:
                    if not dl_resp.ok:
                        log.warning(
                            "sync_materials_download_failed",
                            filename=filename,
                            status=dl_resp.status,
                        )
                        continue
                    dest.write_bytes(await dl_resp.read())
                    log.info("sync_materials_downloaded", filename=filename, dest=str(dest))
            except aiohttp.ClientError as e:
                log.warning("sync_materials_download_error", filename=filename, error=str(e))

    log.info("sync_materials_done", total=len(files))
