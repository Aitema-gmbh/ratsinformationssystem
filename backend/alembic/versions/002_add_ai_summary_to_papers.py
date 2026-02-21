"""Add ai_summary fields to papers table (R1 KI-Kurzfassungen)

Revision ID: 002
Revises: 001
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ai_summary and ai_summary_generated_at columns to papers table."""
    op.add_column('papers', sa.Column('ai_summary', sa.Text(), nullable=True,
                                       comment='KI-generierte Kurzfassung (Claude Haiku)'))
    op.add_column('papers', sa.Column('ai_summary_generated_at', sa.DateTime(), nullable=True,
                                       comment='Zeitstempel der KI-Generierung'))


def downgrade() -> None:
    """Remove ai_summary columns from papers table."""
    op.drop_column('papers', 'ai_summary_generated_at')
    op.drop_column('papers', 'ai_summary')
