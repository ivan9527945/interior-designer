"""啟動時檢查後端是否有新版 Agent 可下載。"""

from __future__ import annotations

from packaging.version import Version

import structlog

from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)

AGENT_VERSION = "0.1.0"


def _is_newer(latest: str, current: str) -> bool:
    """回傳 latest 是否比 current 新；解析失敗則視為不需更新。"""
    try:
        return Version(latest) > Version(current)
    except Exception:
        return False


async def check_for_updates() -> None:
    """呼叫後端 /agent/version，若有新版則 log 提示；任何錯誤皆 graceful fallback。"""
    settings = get_settings()
    url = f"{settings.RS_API_BASE.rstrip('/')}/agent/version"

    try:
        import httpx  # noqa: PLC0415

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)

            if resp.status_code == 404:
                log.debug("update_check_endpoint_not_found", url=url)
                return

            resp.raise_for_status()
            data = resp.json()

    except Exception as exc:
        log.debug("update_check_skipped", reason=str(exc))
        return

    latest = data.get("latest", "")
    download_url = data.get("download_url", "")

    if not latest:
        log.debug("update_check_no_version_field")
        return

    if _is_newer(latest, AGENT_VERSION):
        log.info(
            "update_available",
            current=AGENT_VERSION,
            latest=latest,
            url=download_url,
        )
    else:
        log.debug("update_check_up_to_date", version=AGENT_VERSION)
