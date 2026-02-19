"""
aitema|RIS - Alembic Migration Environment
Multi-tenant aware: can run migrations against specific tenant schemas.
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.core.database import Base

# Import all models so Alembic sees them
from app.models.oparl import (
    System, Body, LegislativeTerm, Organization, Person,
    Membership, Meeting, AgendaItem, Paper, Consultation, File, Location,
)
from app.models.extensions import (
    Template, ApprovalWorkflow, ApprovalWorkflowStep,
    ApprovalInstance, ApprovalDecision, Vote, IndividualVote, FileVersion,
)
from app.models.tenant import Tenant

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL, preferring environment over alembic.ini."""
    return settings.sync_database_url


def get_tenant_schemas() -> list[str]:
    """Get list of tenant schemas to migrate."""
    # Check if a specific schema is requested via -x tenant=schema_name
    tenant = context.get_x_argument(as_dictionary=True).get("tenant")
    if tenant:
        return [tenant]
    return []


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL generation)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations against a connection."""
    tenant_schemas = get_tenant_schemas()

    # Always migrate public schema
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table="alembic_version",
    )
    with context.begin_transaction():
        context.run_migrations()

    # Migrate tenant schemas if specified
    for schema in tenant_schemas:
        connection.execute(text(f'SET search_path TO "{schema}", public'))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table="alembic_version",
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    # Reset search_path
    connection.execute(text("SET search_path TO public"))


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
