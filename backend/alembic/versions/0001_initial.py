"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('admin','designer','viewer')", name="users_role_ck"),
    )

    # projects
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    # files
    op.create_table(
        "files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("s3_key", sa.String, nullable=False),
        sa.Column("kind", sa.String, nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("sha256", sa.String, nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "kind IN ('dwg','dxf','skp','png','exr','vrmat','ref_image','preview')",
            name="files_kind_ck",
        ),
    )
    op.create_index("idx_files_kind", "files", ["kind"])

    # spaces
    op.create_table(
        "spaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("plan_file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("files.id")),
        sa.Column("elevation_file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("files.id")),
        sa.Column("parsed_plan", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # styles
    op.create_table(
        "styles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("kind", sa.String, nullable=False),
        sa.Column("schema_json", postgresql.JSONB, nullable=False),
        sa.Column("thumbnail_file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("files.id")),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('preset','team','personal')", name="styles_kind_ck"),
    )

    # agents
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("machine_name", sa.String, nullable=True),
        sa.Column("os_version", sa.String, nullable=True),
        sa.Column("sketchup_version", sa.String, nullable=True),
        sa.Column("vray_version", sa.String, nullable=True),
        sa.Column("gpu", sa.String, nullable=True),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("allow_foreign_jobs", sa.Boolean, server_default=sa.text("true")),
        sa.Column("token", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_agents_heartbeat", "agents", ["last_heartbeat_at"])

    # renders
    op.create_table(
        "renders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("spaces.id"), nullable=False),
        sa.Column("style_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("styles.id"), nullable=False),
        sa.Column("settings", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("phase_percent", sa.Integer, server_default="0"),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String, nullable=True),
        sa.Column(
            "output_file_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            server_default="{}",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "status IN ('pending','assigned','parsing','modeling','material','rendering','completed','error','cancelled')",
            name="renders_status_ck",
        ),
    )
    op.create_index(
        "idx_renders_status",
        "renders",
        ["status"],
        postgresql_where=sa.text("status NOT IN ('completed','error','cancelled')"),
    )
    op.create_index("idx_renders_space", "renders", ["space_id"])

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("resource_type", sa.String, nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip", postgresql.INET, nullable=True),
        sa.Column("user_agent", sa.String, nullable=True),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index("idx_renders_space", table_name="renders")
    op.drop_index("idx_renders_status", table_name="renders")
    op.drop_table("renders")
    op.drop_index("idx_agents_heartbeat", table_name="agents")
    op.drop_table("agents")
    op.drop_table("styles")
    op.drop_table("spaces")
    op.drop_index("idx_files_kind", table_name="files")
    op.drop_table("files")
    op.drop_table("projects")
    op.drop_table("users")
