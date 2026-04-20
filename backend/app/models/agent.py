import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    machine_name: Mapped[str | None] = mapped_column(String, nullable=True)
    os_version: Mapped[str | None] = mapped_column(String, nullable=True)
    sketchup_version: Mapped[str | None] = mapped_column(String, nullable=True)
    vray_version: Mapped[str | None] = mapped_column(String, nullable=True)
    gpu: Mapped[str | None] = mapped_column(String, nullable=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    allow_foreign_jobs: Mapped[bool] = mapped_column(Boolean, default=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
