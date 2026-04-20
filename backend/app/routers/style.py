import base64
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.deps import CurrentUserDep, DbSession
from app.models.style import Style
from app.schemas.common import CreateStyleRequest, StyleOut
from app.schemas.style import StyleSchema
from app.services.style_engine import parse_text_style, parse_visual_style

router = APIRouter(tags=["style"])


from pydantic import BaseModel  # noqa: E402


class TextStyleBody(BaseModel):
    description: str


@router.post("/style/parse/text", response_model=StyleSchema)
async def parse_text(body: TextStyleBody, user: CurrentUserDep) -> StyleSchema:
    return await parse_text_style(body.description)


@router.post("/style/parse/visual", response_model=StyleSchema)
async def parse_visual(
    description: Annotated[str, Form()],
    images: Annotated[list[UploadFile], File()],
    user: CurrentUserDep,
) -> StyleSchema:
    base64_images: list[str] = []
    for img in images:
        raw_bytes = await img.read()
        base64_images.append(base64.b64encode(raw_bytes).decode("utf-8"))
    return await parse_visual_style(description, base64_images)


@router.get("/styles", response_model=list[StyleOut])
async def list_styles(db: DbSession, user: CurrentUserDep, kind: str | None = None):
    q = select(Style).order_by(Style.created_at)
    if kind:
        q = q.where(Style.kind == kind)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/styles/{style_id}", response_model=StyleOut)
async def get_style(style_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Style, style_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Style not found")
    return row


@router.post("/styles", response_model=StyleOut, status_code=status.HTTP_201_CREATED)
async def create_style(body: CreateStyleRequest, db: DbSession, user: CurrentUserDep):
    valid_kinds = {"preset", "team", "personal"}
    if body.kind not in valid_kinds:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid kind: {body.kind}")
    style = Style(
        name=body.name,
        kind=body.kind,
        schema_json=body.schema_json,
        owner_id=user.id,
    )
    db.add(style)
    await db.commit()
    await db.refresh(style)
    return style
