"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-24 10:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

http_method_enum = sa.Enum("GET", "POST", "HEAD", name="httpmethod")
monitor_status_enum = sa.Enum("unknown", "up", "down", name="monitorstatus")


def upgrade() -> None:
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("method", http_method_enum, nullable=False, server_default="GET"),
        sa.Column("expected_status", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", monitor_status_enum, nullable=False, server_default="unknown"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "monitor_id",
            sa.Integer(),
            sa.ForeignKey("monitors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_checks_monitor_id", "checks", ["monitor_id"])
    op.create_index("ix_checks_checked_at", "checks", ["checked_at"])

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "monitor_id",
            sa.Integer(),
            sa.ForeignKey("monitors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cause", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_incidents_monitor_id", "incidents", ["monitor_id"])


def downgrade() -> None:
    op.drop_index("ix_incidents_monitor_id", table_name="incidents")
    op.drop_table("incidents")

    op.drop_index("ix_checks_checked_at", table_name="checks")
    op.drop_index("ix_checks_monitor_id", table_name="checks")
    op.drop_table("checks")

    op.drop_table("monitors")

    bind = op.get_bind()
    monitor_status_enum.drop(bind, checkfirst=True)
    http_method_enum.drop(bind, checkfirst=True)
