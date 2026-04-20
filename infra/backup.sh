#!/usr/bin/env bash
# RenderStudio 每日備份：Postgres + MinIO
set -euo pipefail

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/renderstudio}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# 確保備份目錄存在
mkdir -p "$BACKUP_DIR"

# Postgres 備份
PGBACKUP="$BACKUP_DIR/postgres_${DATE}.sql.gz"
pg_dump "$DATABASE_URL" | gzip > "$PGBACKUP"
echo "Postgres: $PGBACKUP ($(du -sh "$PGBACKUP" | cut -f1))"

# MinIO 備份（mirror 到本地）
MINIOBACKUP="$BACKUP_DIR/minio_${DATE}"
mc mirror "minio/renderstudio" "$MINIOBACKUP"
echo "MinIO: $MINIOBACKUP"

# 清理舊備份
find "$BACKUP_DIR" -name "postgres_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type d -name "minio_*" -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# 報告
echo "備份完成 $DATE"
