from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file() -> Path:
    """macOS 慣用路徑。"""
    return Path.home() / "Library/Application Support/RenderStudio/.env"


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_env_file()), ".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    RS_API_BASE: str = "http://localhost:8000"
    RS_AGENT_TOKEN: str | None = None

    SKETCHUP_APP: str = "/Applications/SketchUp 2024/SketchUp.app"
    VRAY_VERSION: str = "6.2"

    IDLE_BEFORE_RUN_SECONDS: int = 300
    ALLOW_FOREIGN_JOBS: bool = True

    LOG_LEVEL: str = "INFO"

    DIAG_PORT: int = 9787
    HEARTBEAT_INTERVAL_SECONDS: int = 5
    POLL_TIMEOUT_SECONDS: int = 30


@lru_cache(maxsize=1)
def get_settings() -> AgentSettings:
    return AgentSettings()
