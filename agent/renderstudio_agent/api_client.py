"""與後端 API 通訊。骨架版只有 stub 方法。"""

from typing import Any

import httpx

from renderstudio_agent.config import get_settings


class ApiClient:
    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        self._base = settings.RS_API_BASE
        self._token = token or settings.RS_AGENT_TOKEN
        self._client = httpx.AsyncClient(
            base_url=self._base,
            timeout=settings.POLL_TIMEOUT_SECONDS + 5,
            headers={"Authorization": f"Bearer {self._token}"} if self._token else {},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post("/agent/register", json=payload)
        r.raise_for_status()
        return r.json()

    async def heartbeat(self, payload: dict[str, Any]) -> None:
        await self._client.post("/agent/heartbeat", json=payload)

    async def next_job(self) -> dict[str, Any] | None:
        r = await self._client.get("/agent/next-job")
        if r.status_code == 204:
            return None
        r.raise_for_status()
        data = r.json()
        return data if data else None

    async def report(self, job_id: str, payload: dict[str, Any]) -> None:
        await self._client.post(f"/agent/job/{job_id}/report", json=payload)

    async def report_output(self, job_id: str, file_ids: list[str]) -> None:
        await self._client.post(f"/agent/job/{job_id}/output", json={"fileIds": file_ids})
