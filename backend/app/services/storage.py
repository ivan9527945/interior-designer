"""MinIO / S3 儲存服務。Sprint 1 骨架：stub presigned URL。"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.config import get_settings


def generate_presigned_put(filename: str, content_type: str, kind: str) -> tuple[str, UUID, datetime]:
    """產生 presigned PUT URL。骨架版回假 URL。

    Sprint 1 實作時改用 `minio.Minio.presigned_put_object`。
    """
    settings = get_settings()
    file_id = uuid4()
    # TODO (Sprint 1): 真的呼叫 MinIO client
    scheme = "https" if settings.MINIO_SECURE else "http"
    url = f"{scheme}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{file_id}?X-Amz-Algorithm=stub"
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    return url, file_id, expires_at
