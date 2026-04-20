from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.deps import CurrentUserDep, DbSession
from app.schemas.common import PresignRequest, PresignResponse
from app.services.storage import generate_presigned_put

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/presign", response_model=PresignResponse)
async def presign(body: PresignRequest, user: CurrentUserDep):
    url, file_id, expires_at = generate_presigned_put(body.filename, body.contentType, body.kind)
    return PresignResponse(url=url, fileId=file_id, expiresAt=expires_at)


class CompleteRequest(BaseModel):
    fileId: str


@router.post("/complete")
async def complete(body: CompleteRequest, db: DbSession, user: CurrentUserDep):
    # TODO (Sprint 1): INSERT files row
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
