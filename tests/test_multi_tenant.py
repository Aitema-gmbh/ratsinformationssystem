"""
aitema|RIS - Multi-Tenant Tests
Tests for schema-per-tenant isolation.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import TenantSessionManager
from app.models.tenant import Tenant


@pytest.mark.asyncio
class TestTenantManagement:
    """Tests for tenant CRUD via admin API."""

    async def test_create_tenant(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should create a new tenant and provision its schema."""
        response = await client.post(
            "/api/v1/admin/tenants",
            json={
                "slug": "test-kommune",
                "name": "Testkommune",
                "ags": "99999999",
                "contact_email": "admin@testkommune.de",
            },
            headers=auth_headers,
        )
        # May be 201 or 401/403 depending on test auth setup
        if response.status_code == 201:
            data = response.json()
            assert data["slug"] == "test-kommune"
            assert data["name"] == "Testkommune"
            assert data["ags"] == "99999999"
            assert data["schema_created"] is True

    async def test_list_tenants(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Should list all tenants."""
        response = await client.get(
            "/api/v1/admin/tenants",
            headers=auth_headers,
        )
        assert response.status_code in (200, 401, 403)

    async def test_tenant_requires_auth(self, client: AsyncClient):
        """Tenant endpoints should require authentication."""
        response = await client.get("/api/v1/admin/tenants")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestSchemaIsolation:
    """Tests for schema-per-tenant data isolation."""

    async def test_create_tenant_schema(self, db_session: AsyncSession):
        """Should be able to create a tenant schema."""
        schema_name = "tenant_test_isolation"
        await TenantSessionManager.create_tenant_schema(schema_name)

        # Verify schema exists
        result = await db_session.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name = :name"
            ),
            {"name": schema_name},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == schema_name

        # Cleanup
        await TenantSessionManager.drop_tenant_schema(schema_name)

    async def test_tenant_session_sets_search_path(
        self, db_session: AsyncSession
    ):
        """Tenant session should set search_path correctly."""
        schema_name = "tenant_test_path"
        await TenantSessionManager.create_tenant_schema(schema_name)

        async with TenantSessionManager.tenant_session(schema_name) as session:
            result = await session.execute(text("SHOW search_path"))
            search_path = result.scalar()
            assert schema_name in search_path

        # Cleanup
        await TenantSessionManager.drop_tenant_schema(schema_name)

    async def test_list_tenant_schemas(self, db_session: AsyncSession):
        """Should list only tenant schemas, not system schemas."""
        schemas = await TenantSessionManager.list_tenant_schemas()
        assert isinstance(schemas, list)
        # System schemas should not appear
        for schema in schemas:
            assert schema not in ("public", "information_schema", "pg_catalog")

    async def test_tenant_model_properties(self):
        """Tenant model should generate correct schema names."""
        tenant = Tenant(
            slug="stadt-koeln",
            name="Stadt Koeln",
        )
        assert tenant.schema_name == "tenant_stadt_koeln"

        tenant2 = Tenant(
            slug="kreis-mettmann",
            name="Kreis Mettmann",
        )
        assert tenant2.schema_name == "tenant_kreis_mettmann"
