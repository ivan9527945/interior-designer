from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUserDep, DbSession

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.post("/{space_id}/parse")
async def trigger_parse(space_id: str, db: DbSession, user: CurrentUserDep):
    # TODO (Sprint 2): enqueue DXF parse job
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{space_id}/parsed")
async def get_parsed(space_id: str, db: DbSession, user: CurrentUserDep):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
