from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentUserDep, DbSession
from app.models.space import Space
from app.schemas.common import SpaceOut
from app.services.job_dispatcher import enqueue

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("/{space_id}", response_model=SpaceOut)
async def get_space(space_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Space, space_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Space not found")
    return row


@router.post("/{space_id}/parse")
async def trigger_parse(space_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Space, space_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Space not found")
    await enqueue({"type": "parse", "space_id": str(space_id)})
    return {"jobId": str(space_id), "status": "queued"}


@router.get("/{space_id}/parsed")
async def get_parsed(space_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Space, space_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Space not found")
    if not row.parsed_plan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parsing not done yet")
    return row.parsed_plan
