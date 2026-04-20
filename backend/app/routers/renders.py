import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import CurrentUserDep, DbSession
from app.models.render import Render
from app.models.share_token import ShareToken
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


@router.post("/{render_id}/retry", response_model=RenderOut, status_code=status.HTTP_201_CREATED)
async def retry_render(render_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Render, render_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")
    if row.status not in ("error", "cancelled"):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Cannot retry render in status {row.status}; must be error or cancelled",
        )

    style = await db.get(Style, row.style_id)

    new_render = Render(
        space_id=row.space_id,
        style_id=row.style_id,
        settings=row.settings,
        status="pending",
    )
    db.add(new_render)
    await db.commit()
    await db.refresh(new_render)

    await enqueue({
        "id": str(new_render.id),
        "space_id": str(new_render.space_id),
        "style_id": str(new_render.style_id),
        "settings": new_render.settings,
        "style_schema": style.schema_json if style else {},
    })
    return new_render


class ShareTokenOut(BaseModel):
    token: str
    url: str
    expiresAt: datetime


@router.post("/{render_id}/share", response_model=ShareTokenOut, status_code=status.HTTP_201_CREATED)
async def create_share(render_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Render, render_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")

    from app.config import get_settings
    settings = get_settings()

    token_str = secrets.token_urlsafe(24)
    expires_at = datetime.now(UTC) + timedelta(days=7)

    share = ShareToken(
        render_id=render_id,
        token=token_str,
        expires_at=expires_at,
    )
    db.add(share)
    await db.commit()

    return ShareTokenOut(
        token=token_str,
        url=f"/share/{token_str}",
        expiresAt=expires_at,
    )


@router.get("/{render_id}/share", response_model=ShareTokenOut)
async def get_share(render_id: UUID, db: DbSession, user: CurrentUserDep):
    now = datetime.now(UTC)
    result = await db.execute(
        select(ShareToken)
        .where(ShareToken.render_id == render_id)
        .where(ShareToken.expires_at > now)
        .order_by(ShareToken.created_at.desc())
        .limit(1)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No active share token found")

    return ShareTokenOut(
        token=share.token,
        url=f"/share/{share.token}",
        expiresAt=share.expires_at,
    )
