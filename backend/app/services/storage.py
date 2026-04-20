"""MinIO / S3 儲存服務。

有 MinIO 可用時產真 presigned URL；失敗則 fallback stub，讓純前端 dev 能跑。
"""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID, uuid4

import structlog
from minio import Minio
from minio.error import S3Error

from app.config import get_settings

log = structlog.get_logger(__name__)


@lru_cache(maxsize=1)
def _client() -> Minio:
    s = get_settings()
    return Minio(
        endpoint=s.MINIO_ENDPOINT,
        access_key=s.MINIO_ACCESS_KEY,
        secret_key=s.MINIO_SECRET_KEY,
        secure=s.MINIO_SECURE,
    )


def _ensure_bucket() -> str:
    s = get_settings()
    bucket = s.MINIO_BUCKET
    try:
        c = _client()
        if not c.bucket_exists(bucket):
            c.make_bucket(bucket)
    except (S3Error, Exception) as e:  # noqa: BLE001
        log.warning("minio_ensure_bucket_failed", error=str(e))
    return bucket


def _object_key(file_id: UUID, filename: str, kind: str) -> str:
    safe = filename.replace("/", "_").replace("\\", "_")
    return f"{kind}/{file_id}/{safe}"


def generate_presigned_put(
    filename: str, content_type: str, kind: str
) -> tuple[str, UUID, datetime, str]:
    """回 (url, file_id, expires_at, object_key)。

    MinIO 不通時會 fallback 給一個不可用但格式正確的 stub URL，讓前端 UI 流程能跑。
    """
    settings = get_settings()
    file_id = uuid4()
    key = _object_key(file_id, filename, kind)
    expires = timedelta(minutes=15)
    expires_at = datetime.now(UTC) + expires

    bucket = _ensure_bucket()
    try:
        url = _client().presigned_put_object(bucket, key, expires=expires)
        return url, file_id, expires_at, key
    except (S3Error, Exception) as e:  # noqa: BLE001
        log.warning("minio_presign_failed_fallback_stub", error=str(e))
        scheme = "https" if settings.MINIO_SECURE else "http"
        url = f"{scheme}://{settings.MINIO_ENDPOINT}/{bucket}/{key}?X-Amz-Algorithm=stub"
        return url, file_id, expires_at, key


def generate_presigned_get(key: str, expires_minutes: int = 60) -> str:
    """產給前端看的 GET URL（如 gallery 預覽）。失敗時回 key 本身避免爆頁。"""
    s = get_settings()
    try:
        return _client().presigned_get_object(
            s.MINIO_BUCKET, key, expires=timedelta(minutes=expires_minutes)
        )
    except (S3Error, Exception) as e:  # noqa: BLE001
        log.warning("minio_presign_get_failed", error=str(e))
        scheme = "https" if s.MINIO_SECURE else "http"
        return f"{scheme}://{s.MINIO_ENDPOINT}/{s.MINIO_BUCKET}/{key}"
