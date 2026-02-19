"""
aitema|RIS - Tenant Model
Multi-tenancy support with schema-per-tenant isolation.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tenant(Base):
    """
    A tenant represents a single municipality (Kommune) or governmental body.
    Each tenant gets its own PostgreSQL schema for data isolation.

    The tenant table lives in the 'public' schema and is shared across all tenants.
    """
    __tablename__ = "tenant"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Unique slug used as PostgreSQL schema name
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
        doc="URL-safe identifier, also used as DB schema name (e.g. 'stadt-koeln')"
    )
    name: Mapped[str] = mapped_column(
        String(512), nullable=False,
        doc="Display name (e.g. 'Stadt Koeln')"
    )
    # AGS (Amtlicher Gemeindeschluessel) - unique German municipality code
    ags: Mapped[Optional[str]] = mapped_column(
        String(12), unique=True, nullable=True,
        doc="Amtlicher Gemeindeschluessel"
    )
    # Configuration
    domain: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True,
        doc="Custom domain for this tenant (e.g. ris.stadt-koeln.de)"
    )
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict,
        doc="Tenant-specific configuration (branding, features, etc.)"
    )
    # Keycloak realm mapping
    keycloak_realm: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        doc="Keycloak realm for this tenant (if separate realm)"
    )
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_trial: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Whether this is a trial/demo tenant"
    )
    # Contact
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    schema_created: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Whether the tenant DB schema has been created"
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_tenant_name", "name"),
        Index("ix_tenant_ags", "ags"),
        Index("ix_tenant_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Tenant(slug={self.slug!r}, name={self.name!r})>"

    @property
    def schema_name(self) -> str:
        """PostgreSQL schema name for this tenant."""
        return f"tenant_{self.slug.replace('-', '_')}"
