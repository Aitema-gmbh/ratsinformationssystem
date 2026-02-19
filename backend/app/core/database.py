"""
aitema|RIS - Database Configuration
Async SQLAlchemy with Schema-per-Tenant multi-tenancy.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class TenantSessionManager:
    """
    Manages database sessions with schema-per-tenant isolation.
    
    Each tenant gets their own PostgreSQL schema containing all OParl tables.
    The public schema contains shared tables (tenants, users, etc.).
    """

    DEFAULT_SCHEMA = "public"

    @staticmethod
    async def create_tenant_schema(schema_name: str) -> None:
        """Create a new schema for a tenant and set up all required tables."""
        async with engine.begin() as conn:
            await conn.execute(text(fCREATE SCHEMA IF NOT EXISTS {schema_name}))
            # Tables will be created by Alembic migrations
            # running against this schema

    @staticmethod
    async def drop_tenant_schema(schema_name: str) -> None:
        """Drop a tenant schema (DANGER: irreversible)."""
        async with engine.begin() as conn:
            await conn.execute(text(fDROP SCHEMA IF EXISTS {schema_name} CASCADE))

    @staticmethod
    async def list_tenant_schemas() -> list[str]:
        """List all tenant schemas (excludes system schemas)."""
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    "SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name NOT IN (public, information_schema, pg_catalog, pg_toast, keycloak) "
                    "AND schema_name NOT LIKE pg_%"
                )
            )
            return [row[0] for row in result.fetchall()]

    @staticmethod
    @asynccontextmanager
    async def tenant_session(schema_name: str) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a database session scoped to a specific tenant schema.
        
        Sets the PostgreSQL search_path to the tenant schema so all queries
        automatically operate on the correct tenant data.
        """
        async with async_session_factory() as session:
            try:
                # Set search_path to tenant schema, falling back to public
                await session.execute(
                    text(fSET search_path TO {schema_name}, public)
                )
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                # Reset search_path
                await session.execute(text("SET search_path TO public"))
                await session.close()


async def get_tenant_db(tenant_schema: str) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a tenant-scoped database session."""
    async with TenantSessionManager.tenant_session(tenant_schema) as session:
        yield session


async def init_db() -> None:
    """Initialize database - create public schema tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
