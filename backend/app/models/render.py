import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Render(Base):
    __tablename__ = "renders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    space_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("spaces.id"), nullable=False)
    style_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("styles.id"), nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    phase_percent: Mapped[int] = mapped_column(Integer, default=0)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    output_file_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','assigned','parsing','modeling','material','rendering','completed','error','cancelled')",
            name="renders_status_ck",
        ),
    )
