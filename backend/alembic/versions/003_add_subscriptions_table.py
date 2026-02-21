"""add subscriptions table (D5 Buerger-Abonnement)

Revision ID: 003
Revises: 002
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("subscription_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        sa.Column("target_label", sa.String(255), nullable=True),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("confirm_token", sa.String(100), nullable=False, unique=True),
        sa.Column("unsubscribe_token", sa.String(100), nullable=False, unique=True),
        sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_subscriptions_email", "subscriptions", ["email"])
    op.create_index("ix_subscriptions_type_target", "subscriptions", ["subscription_type", "target_id"])


def downgrade() -> None:
    op.drop_index("ix_subscriptions_type_target", table_name="subscriptions")
    op.drop_index("ix_subscriptions_email", table_name="subscriptions")
    op.drop_table("subscriptions")
