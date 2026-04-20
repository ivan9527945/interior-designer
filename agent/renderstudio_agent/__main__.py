"""Agent entry — Sprint 0/1 真實 execute_job 流程。"""

from __future__ import annotations

import asyncio
import platform
import tempfile
from pathlib import Path

import structlog

from renderstudio_agent.api_client import ApiClient
from renderstudio_agent.config import get_settings
from renderstudio_agent.diag_server import start_diag_server
from renderstudio_agent.heartbeat import heartbeat_loop
from renderstudio_agent.poller import poll_next_job
from renderstudio_agent.utils import configure_logging

log = structlog.get_logger(__name__)


async def register_or_resume(client: ApiClient) -> str:
    settings = get_settings()
    mac_ver = platform.mac_ver()[0] or "unknown"

    # Token 已存在 → 跳過重新註冊
    if settings.RS_AGENT_TOKEN:
        log.info("agent_resume_with_existing_token")
        return "resumed"

    log.info("agent_registering", api_base=settings.RS_API_BASE)
    resp = await client.register({
        "machineName": platform.node(),
        "osVersion": f"macOS {mac_ver}",
        "sketchupVersion": "2024",
        "vrayVersion": settings.VRAY_VERSION,
        "gpu": None,
    })
    agent_id = resp["agentId"]
    token = resp["token"]

    # 寫入 ~/.env 方便下次復用
    env_file = Path.home() / "Library/Application Support/RenderStudio/.env"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(
        f"RS_API_BASE={settings.RS_API_BASE}\nRS_AGENT_TOKEN={token}\n",
        encoding="utf-8",
    )
    log.info("agent_registered", agent_id=agent_id)
    return agent_id


async def execute_job(client: ApiClient, job: dict) -> None:
    """完整執行一個渲染 job。"""
    from renderstudio_agent.parsers.dxf_parser import parse  # noqa: PLC0415
    from renderstudio_agent.parsers.dwg_converter import convert  # noqa: PLC0415
    from renderstudio_agent.parsers.plan_elevation_merge import merge  # noqa: PLC0415
    from renderstudio_agent.sketchup.controller import (  # noqa: PLC0415
        apply_materials,
        generate_model,
        trigger_render,
    )
    from renderstudio_agent.vray.adapter import apply_preset  # noqa: PLC0415
    from renderstudio_agent.vray.style_to_vray import map_style  # noqa: PLC0415

    job_id = job["id"]
    settings_cfg = job.get("settings", {})
    quality = settings_cfg.get("quality", "standard")
    style_schema = job.get("style_schema", {})

    async def report(status: str, phase: str | None = None, percent: int = 0, error: str | None = None) -> None:
        try:
            await client.report(job_id, {"status": status, "phase": phase, "percent": percent, "error": error})
        except Exception as e:
            log.warning("report_failed", error=str(e))

    with tempfile.TemporaryDirectory(prefix="rs_job_") as tmpdir:
        tmp = Path(tmpdir)

        try:
            await report("assigned", "setup", 5)

            # ── 1. 取 DWG/DXF 檔 ─────────────────────────────────────
            # 未來：從 MinIO 下載。現在假設 dwg_path/dxf_path 在 job dict。
            dxf_path: Path | None = None
            if "dxf_path" in job:
                dxf_path = Path(job["dxf_path"])
            elif "dwg_path" in job:
                dwg_path = Path(job["dwg_path"])
                dxf_path = convert(dwg_path, tmp / "dxf")

            if dxf_path is None or not dxf_path.exists():
                raise FileNotFoundError("No DXF/DWG path in job")

            # ── 2. DXF 解析 ───────────────────────────────────────────
            await report("parsing", "dxf", 15)
            plan_data = parse(dxf_path)
            scene = merge(plan_data)

            # ── 3. 建模 ───────────────────────────────────────────────
            await report("modeling", "sketchup", 35)
            skp_base = tmp / "model.skp"
            await generate_model(scene, skp_base)

            # ── 4. 套材質 ─────────────────────────────────────────────
            await report("material", "material", 55)
            skp_mat = tmp / "model_mat.skp"
            await apply_materials(skp_base, style_schema, skp_mat)

            # ── 5. V-Ray 渲染 ─────────────────────────────────────────
            await report("rendering", "vray", 70)
            vray_base = apply_preset(quality)
            vray_style = map_style(style_schema)
            vray_params = {**vray_base, **vray_style}
            output_png = tmp / "output.png"
            await trigger_render(skp_mat, vray_params, output_png)

            # ── 6. 上傳結果 ───────────────────────────────────────────
            await report("rendering", "upload", 90)
            file_ids = await _upload_output(client, output_png, job_id)

            await client.report_output(job_id, file_ids)
            await report("completed", "done", 100)
            log.info("job_completed", job_id=job_id)

        except Exception as e:
            log.exception("job_failed", job_id=job_id, error=str(e))
            await report("error", error=str(e))


async def _upload_output(client: ApiClient, png: Path, job_id: str) -> list[str]:
    """PNG 上傳到 MinIO（透過後端 presign）。回傳 file_id list。"""
    if not png.exists():
        log.warning("output_png_missing", path=str(png))
        return []

    import httpx  # noqa: PLC0415

    settings = get_settings()
    async with httpx.AsyncClient(
        base_url=settings.RS_API_BASE,
        timeout=300,
        headers={"Authorization": f"Bearer {settings.RS_AGENT_TOKEN}"} if settings.RS_AGENT_TOKEN else {},
    ) as http:
        # 1) presign
        r = await http.post("/uploads/presign", json={
            "filename": f"render_{job_id}.png",
            "contentType": "image/png",
            "kind": "png",
        })
        r.raise_for_status()
        presign = r.json()
        url = presign["url"]
        file_id = presign["fileId"]

        # 2) PUT to MinIO
        data = png.read_bytes()
        await http.put(url, content=data, headers={"Content-Type": "image/png"})

        # 3) complete
        await http.post("/uploads/complete", json={
            "fileId": file_id,
            "filename": f"render_{job_id}.png",
            "kind": "png",
            "sizeBytes": len(data),
        })

    return [file_id]


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    client = ApiClient()
    agent_id = await register_or_resume(client)

    diag_server = await start_diag_server()
    heartbeat_task = asyncio.create_task(heartbeat_loop(client, agent_id))

    try:
        while True:
            log.debug("polling")
            try:
                job = await poll_next_job(client)
                if job:
                    await execute_job(client, job)
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
