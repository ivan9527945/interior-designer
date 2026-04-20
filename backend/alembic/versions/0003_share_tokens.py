"""add share_tokens table

Revision ID: 0003
Revises: 0001
Create Date: 2026-04-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "share_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "render_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("renders.id"),
            nullable=False,
        ),
        sa.Column("token", sa.String(), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("view_count", sa.Integer(), default=0),
    )
    op.create_index("idx_share_tokens_token", "share_tokens", ["token"])


def downgrade() -> None:
    op.drop_index("idx_share_tokens_token", table_name="share_tokens")
    op.drop_table("share_tokens")
