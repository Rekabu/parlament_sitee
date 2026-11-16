"""add calendar event table

Revision ID: fb243b779b53
Revises: ec6bd3a55566
Create Date: 2026-11-16 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "fb243b779b53"
down_revision: Union[str, Sequence[str], None] = "ec6bd3a55566"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "calendar_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("location", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("all_day", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calendar_event_starts_at"), "calendar_event", ["starts_at"], unique=False)
    op.create_index(op.f("ix_calendar_event_title"), "calendar_event", ["title"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_event_title"), table_name="calendar_event")
    op.drop_index(op.f("ix_calendar_event_starts_at"), table_name="calendar_event")
    op.drop_table("calendar_event")
