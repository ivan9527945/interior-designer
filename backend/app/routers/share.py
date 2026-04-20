"""公開分享頁 API — 無需驗證。"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import DbSession
from app.models.render import Render
from app.models.share_token import ShareToken
from app.schemas.common import RenderOut

router = APIRouter(prefix="/share", tags=["share"])


class SharedRenderOut(BaseModel):
    render: RenderOut
    expiresAt: datetime


@router.get("/{token}", response_model=SharedRenderOut)
async def get_shared_render(token: str, db: DbSession):
    now = datetime.now(UTC)

    result = await db.execute(
        select(ShareToken).where(ShareToken.token == token)
    )
    share = result.scalar_one_or_none()

    if not share:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Share token not found")
    if share.expires_at.replace(tzinfo=UTC) <= now if share.expires_at.tzinfo is None else share.expires_at <= now:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Share token has expired")

    # increment view count
    share.view_count = (share.view_count or 0) + 1
    await db.commit()

    render = await db.get(Render, share.render_id)
    if not render:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Render not found")

    return SharedRenderOut(
        render=RenderOut.model_validate(render),
        expiresAt=share.expires_at,
    )
