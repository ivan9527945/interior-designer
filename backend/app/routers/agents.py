import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import DbSession
from app.models.agent import Agent
from app.models.file import File
from app.models.render import Render
from app.schemas.common import (
    AgentHeartbeat,
    AgentRegisterRequest,
    AgentRegisterResponse,
    JobOutput,
    JobReport,
)
from app.services.job_dispatcher import pop
from app.services.slack import notify_slack
from app.services.sse_broker import publish

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/register", response_model=AgentRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(body: AgentRegisterRequest, db: DbSession):
    token = secrets.token_urlsafe(32)
    agent = Agent(
        machine_name=body.machineName,
        os_version=body.osVersion,
        sketchup_version=body.sketchupVersion,
        vray_version=body.vrayVersion,
        gpu=body.gpu,
        token=token,
        last_heartbeat_at=datetime.now(UTC),
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentRegisterResponse(agentId=agent.id, token=token)


@router.post("/heartbeat")
async def heartbeat(body: AgentHeartbeat, db: DbSession):
    agent = await db.get(Agent, body.agentId)
    if not agent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Agent not found")
    agent.last_heartbeat_at = datetime.now(UTC)
    await db.commit()
    return {"ok": True}


@router.get("/next-job")
async def next_job():
    job = await pop()
    if job is None:
        return None
    return job


@router.post("/job/{job_id}/report")
async def report_job(job_id: UUID, body: JobReport, db: DbSession):
    render = await db.get(Render, job_id)
    if not render:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")

    render.status = body.status
    if body.percent is not None:
        render.phase_percent = body.percent
    if body.error:
        render.error_message = body.error
    if body.status in ("completed", "error", "cancelled") and not render.finished_at:
        render.finished_at = datetime.now(UTC)
    if body.status == "assigned" and not render.started_at:
        render.started_at = datetime.now(UTC)

    await db.commit()

    if body.status == "completed":
        import asyncio
        asyncio.create_task(
            notify_slack(
                render_id=str(job_id),
                message=f":white_check_mark: Render `{job_id}` 已完成渲染。",
            )
        )

    await publish(str(job_id), {
        "event": body.status if body.status in ("completed", "error", "cancelled") else "progress",
        "data": {
            "status": body.status,
            "percent": body.percent,
            "phase": body.phase,
            "error": body.error,
        },
    })
    return {"ok": True}


@router.post("/job/{job_id}/output")
async def report_output(job_id: UUID, body: JobOutput, db: DbSession):
    render = await db.get(Render, job_id)
    if not render:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")

    existing = list(render.output_file_ids or [])
    for fid in body.fileIds:
        if fid not in existing:
            existing.append(fid)
    render.output_file_ids = existing
    await db.commit()
    return {"ok": True, "count": len(existing)}


@router.get("/status")
async def agent_status(db: DbSession):
    """回傳最近 30 秒內有心跳的 agents（供前端顯示綠點）。"""
    cutoff = datetime.now(UTC) - timedelta(seconds=30)
    result = await db.execute(
        select(Agent).where(Agent.last_heartbeat_at >= cutoff)
    )
    agents = result.scalars().all()
    return {
        "online": len(agents) > 0,
        "count": len(agents),
        "agents": [
            {
                "id": str(a.id),
                "machineName": a.machine_name,
                "lastHeartbeat": a.last_heartbeat_at.isoformat() if a.last_heartbeat_at else None,
            }
            for a in agents
        ],
    }
