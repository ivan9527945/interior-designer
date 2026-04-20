from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.deps import CurrentUserDep, DbSession
from app.schemas.common import StyleOut
from app.schemas.style import StyleSchema
from app.services.style_engine import parse_text_style, parse_visual_style

router = APIRouter(tags=["style"])


class TextStyleRequest(BaseModel):
    description: str


@router.post("/style/parse/text", response_model=StyleSchema)
async def parse_text(body: TextStyleRequest, user: CurrentUserDep) -> StyleSchema:
    return await parse_text_style(body.description)


@router.post("/style/parse/visual", response_model=StyleSchema)
async def parse_visual(description: str, images: list[UploadFile], user: CurrentUserDep) -> StyleSchema:
    # TODO (Sprint 3): 上傳 images 到 MinIO，拿到 URL 再餵給 Claude Vision
    image_urls: list[str] = []
    return await parse_visual_style(description, image_urls)


@router.get("/styles", response_model=list[StyleOut])
async def list_styles(db: DbSession, user: CurrentUserDep, kind: str | None = None):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/styles", response_model=StyleOut, status_code=status.HTTP_201_CREATED)
async def create_style(db: DbSession, user: CurrentUserDep):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
