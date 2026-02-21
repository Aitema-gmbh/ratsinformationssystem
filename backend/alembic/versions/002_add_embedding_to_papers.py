"""Add vector embedding column to papers for semantic search.

Revision ID: 002
Revises: 001
Create Date: 2026-02-21

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
    # Activate pgvector extension (safe if already exists)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add 1024-dim embedding column (voyage-3 dimension)
    op.execute(
        "ALTER TABLE papers ADD COLUMN IF NOT EXISTS embedding vector(1024)"
    )

    # IVFFlat index for fast cosine similarity search
    # lists=100 is good for up to ~1M rows; adjust for larger datasets
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_papers_embedding_cosine "
        "ON papers USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_papers_embedding_cosine")
    op.execute("ALTER TABLE papers DROP COLUMN IF EXISTS embedding")
