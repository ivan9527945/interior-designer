from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import CurrentUserDep, DbSession
from app.models.render import Render
from app.models.space import Space
from app.models.style import Style
from app.schemas.common import RenderOut
from app.services.job_dispatcher import enqueue
from app.services.sse_broker import publish

router = APIRouter(prefix="/renders", tags=["renders"])


class CreateRenderRequest(BaseModel):
    spaceId: UUID
    styleId: UUID
    settings: dict


@router.post("", response_model=RenderOut, status_code=status.HTTP_201_CREATED)
async def create_render(body: CreateRenderRequest, db: DbSession, user: CurrentUserDep):
    space = await db.get(Space, body.spaceId)
    if not space:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Space not found")
    style = await db.get(Style, body.styleId)
    if not style:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Style not found")

    render = Render(
        space_id=body.spaceId,
        style_id=body.styleId,
        settings=body.settings,
        status="pending",
    )
    db.add(render)
    await db.commit()
    await db.refresh(render)

    await enqueue({
        "id": str(render.id),
        "space_id": str(render.space_id),
        "style_id": str(render.style_id),
        "settings": render.settings,
        "style_schema": style.schema_json,
    })
    return render


@router.get("", response_model=list[RenderOut])
async def list_renders(
    db: DbSession,
    user: CurrentUserDep,
    renderStatus: str | None = None,
    spaceId: UUID | None = None,
):
    q = select(Render).order_by(Render.created_at.desc())
    if renderStatus:
        q = q.where(Render.status == renderStatus)
    if spaceId:
        q = q.where(Render.space_id == spaceId)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{render_id}", response_model=RenderOut)
async def get_render(render_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Render, render_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")
    return row


@router.delete("/{render_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_render(render_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Render, render_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")
    if row.status in ("completed", "error", "cancelled"):
        raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot cancel render in status {row.status}")
    row.status = "cancelled"
    await db.commit()
    await publish(str(render_id), {"event": "cancelled", "data": {"status": "cancelled"}})
