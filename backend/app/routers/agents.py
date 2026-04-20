from fastapi import APIRouter, HTTPException, status

from app.deps import DbSession
from app.schemas.common import (
    AgentHeartbeat,
    AgentRegisterRequest,
    AgentRegisterResponse,
    JobReport,
)
from app.services.job_dispatcher import pop

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/register", response_model=AgentRegisterResponse)
async def register(body: AgentRegisterRequest, db: DbSession):
    # TODO (Sprint 2): INSERT agents，發 token
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/heartbeat")
async def heartbeat(body: AgentHeartbeat, db: DbSession):
    # TODO (Sprint 2): UPDATE agents SET last_heartbeat_at=now()
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/next-job")
async def next_job():
    """Long-poll 取任務。骨架版立刻回 null。"""
    job = await pop()
    return job  # None or dict


@router.post("/job/{job_id}/report")
async def report_job(job_id: str, body: JobReport):
    # TODO (Sprint 2): UPDATE renders + publish SSE event
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/job/{job_id}/output")
async def report_output(job_id: str):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
