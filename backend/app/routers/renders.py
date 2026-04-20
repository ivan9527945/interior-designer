from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.deps import CurrentUserDep, DbSession
from app.schemas.common import RenderOut

router = APIRouter(prefix="/renders", tags=["renders"])


class CreateRenderRequest(BaseModel):
    spaceId: str
    styleId: str
    settings: dict


@router.post("", response_model=RenderOut, status_code=status.HTTP_201_CREATED)
async def create_render(body: CreateRenderRequest, db: DbSession, user: CurrentUserDep):
    # TODO (Sprint 2): INSERT render + enqueue Redis job
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.get("", response_model=list[RenderOut])
async def list_renders(
    db: DbSession,
    user: CurrentUserDep,
    status: str | None = None,
    spaceId: str | None = None,
):
    raise HTTPException(501, "Not Implemented")


@router.get("/{render_id}", response_model=RenderOut)
async def get_render(render_id: str, db: DbSession, user: CurrentUserDep):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
