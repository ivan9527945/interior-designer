from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://renderstudio:renderstudio@localhost:5432/renderstudio"
    REDIS_URL: str = "redis://localhost:6379/0"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "renderstudio"
    MINIO_SECURE: bool = False

    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    KEYCLOAK_ISSUER: str = ""
    KEYCLOAK_AUDIENCE: str = "renderstudio"

    SSE_KEEPALIVE_SECONDS: int = 15
    JOB_LONG_POLL_TIMEOUT: int = 30

    LOG_LEVEL: str = "INFO"

    SLACK_WEBHOOK_URL: str | None = None
    SHARE_BASE_URL: str = "http://localhost:3001"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
