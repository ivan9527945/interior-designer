from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUserDep, DbSession
from app.models.file import File
from app.schemas.common import PresignRequest, PresignResponse, UploadCompleteRequest
from app.services.storage import generate_presigned_put

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/presign", response_model=PresignResponse)
async def presign(body: PresignRequest, user: CurrentUserDep):
    url, file_id, expires_at, _key = generate_presigned_put(body.filename, body.contentType, body.kind)
    return PresignResponse(url=url, fileId=file_id, expiresAt=expires_at)


@router.post("/complete", status_code=status.HTTP_201_CREATED)
async def complete(body: UploadCompleteRequest, db: DbSession, user: CurrentUserDep):
    _valid_kinds = {"dwg", "dxf", "skp", "png", "exr", "vrmat", "ref_image", "preview"}
    if body.kind not in _valid_kinds:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid kind: {body.kind}")

    from app.services.storage import _object_key  # noqa: PLC0415
    key = _object_key(body.fileId, body.filename, body.kind)

    file_row = File(
        id=body.fileId,
        s3_key=key,
        kind=body.kind,
        size_bytes=body.sizeBytes,
        sha256=body.sha256,
        owner_id=user.id,
    )
    db.add(file_row)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return {"ok": True, "fileId": str(body.fileId)}
