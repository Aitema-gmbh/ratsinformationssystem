"""add simple_language to papers

Revision ID: 002
Revises: 001
Create Date: 2026-02-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "papers",
        sa.Column("simple_language_text", sa.Text(), nullable=True,
                  comment="KI-generierte einfache Sprache (A2)"),
    )
    op.add_column(
        "papers",
        sa.Column("simple_language_generated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("papers", "simple_language_generated_at")
    op.drop_column("papers", "simple_language_text")
