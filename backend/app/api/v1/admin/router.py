"""
aitema|RIS - Admin API Endpoints
Tenant management, user administration, system configuration.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import TenantSessionManager, get_db
from app.core.security import Role, require_role, TokenPayload
from app.models.tenant import Tenant

router = APIRouter()


# ===================================================================
# Schemas
# ===================================================================

class TenantCreate(BaseModel):
    slug: str
    name: str
    ags: str | None = None
    domain: str | None = None
    contact_email: str | None = None
    contact_name: str | None = None
    config: dict = {}


class TenantUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    contact_email: str | None = None
    contact_name: str | None = None
    config: dict | None = None
    is_active: bool | None = None


class TenantResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    ags: str | None
    domain: str | None
    is_active: bool
    is_trial: bool
    schema_created: bool
    contact_email: str | None
    contact_name: str | None

    model_config = {"from_attributes": True}


# ===================================================================
# Tenant Management
# ===================================================================

@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.SUPERADMIN)),
):
    """List all tenants (superadmin only)."""
    result = await db.execute(select(Tenant).order_by(Tenant.name))
    tenants = result.scalars().all()
    return tenants


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.SUPERADMIN)),
):
    """
    Create a new tenant and provision its database schema.
    This creates a new PostgreSQL schema with all OParl tables.
    """
    # Check for duplicate slug
    existing = await db.execute(select(Tenant).where(Tenant.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant with slug '{data.slug}' already exists",
        )

    tenant = Tenant(
        slug=data.slug,
        name=data.name,
        ags=data.ags,
        domain=data.domain,
        contact_email=data.contact_email,
        contact_name=data.contact_name,
        config=data.config,
    )
    db.add(tenant)
    await db.flush()

    # Create the tenant's database schema
    await TenantSessionManager.create_tenant_schema(tenant.schema_name)
    tenant.schema_created = True

    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.SUPERADMIN)),
):
    """Get a single tenant by ID."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.SUPERADMIN)),
):
    """Update a tenant's configuration."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tenant, key, value)

    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.SUPERADMIN)),
):
    """
    Deactivate a tenant (soft delete).
    Does NOT drop the database schema - use purge for that.
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.is_active = False
    await db.commit()


# ===================================================================
# System Status
# ===================================================================

@router.get("/status")
async def system_status(
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_role(Role.ADMIN)),
):
    """Get system status information."""
    result = await db.execute(select(Tenant).where(Tenant.is_active == True))
    active_tenants = len(result.scalars().all())

    schemas = await TenantSessionManager.list_tenant_schemas()

    return {
        "status": "operational",
        "active_tenants": active_tenants,
        "schemas": schemas,
    }
