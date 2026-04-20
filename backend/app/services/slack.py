import httpx
import structlog

log = structlog.get_logger()


async def notify_slack(render_id: str, message: str) -> None:
    from app.config import get_settings

    url = get_settings().SLACK_WEBHOOK_URL
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            await c.post(url, json={"text": message})
    except Exception as e:
        log.warning("slack_notify_failed", error=str(e))
