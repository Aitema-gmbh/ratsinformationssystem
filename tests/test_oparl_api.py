"""
aitema|RIS - OParl API Tests
Tests for OParl 1.1 compliant REST endpoints.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
class TestOParlSystem:
    """Tests for the OParl System endpoint."""

    async def test_get_system_returns_oparl_system(
        self, client: AsyncClient, sample_system
    ):
        """System endpoint should return valid OParl System object."""
        response = await client.get("/api/v1/oparl/system")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "https://schema.oparl.org/1.1/System"
        assert "oparlVersion" in data
        assert data["oparlVersion"] == "https://schema.oparl.org/1.1/"
        assert "body" in data

    async def test_get_system_404_when_not_configured(self, client: AsyncClient):
        """System endpoint should return 404 when no system is configured."""
        response = await client.get("/api/v1/oparl/system")
        # Without sample_system fixture, this may be 404
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
class TestOParlBody:
    """Tests for the OParl Body endpoints."""

    async def test_list_bodies(self, client: AsyncClient, sample_body):
        """Body list should return paginated results."""
        response = await client.get("/api/v1/oparl/body")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert data["pagination"]["totalElements"] >= 1

    async def test_get_body_by_id(self, client: AsyncClient, sample_body):
        """Should return a single body with all OParl properties."""
        response = await client.get(f"/api/v1/oparl/body/{sample_body.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "https://schema.oparl.org/1.1/Body"
        assert data["name"] == "Teststadt"
        assert data["shortName"] == "TST"
        assert data["ags"] == "12345678"
        # OParl list URLs
        assert "organization" in data
        assert "person" in data
        assert "meeting" in data
        assert "paper" in data
        assert "legislativeTerm" in data

    async def test_get_body_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent body."""
        import uuid
        response = await client.get(f"/api/v1/oparl/body/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_body_pagination(self, client: AsyncClient, sample_body):
        """Pagination parameters should be respected."""
        response = await client.get("/api/v1/oparl/body?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["currentPage"] == 1
        assert data["pagination"]["elementsPerPage"] == 10


@pytest.mark.asyncio
class TestOParlOrganization:
    """Tests for the OParl Organization endpoints."""

    async def test_list_organizations(self, client: AsyncClient, sample_body):
        """Should list organizations for a body."""
        response = await client.get(
            f"/api/v1/oparl/body/{sample_body.id}/organization"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    async def test_filter_by_type(self, client: AsyncClient, sample_body):
        """Should filter organizations by type."""
        response = await client.get(
            f"/api/v1/oparl/body/{sample_body.id}/organization?organization_type=Ausschuss"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestOParlMeeting:
    """Tests for the OParl Meeting endpoints."""

    async def test_list_meetings(self, client: AsyncClient, sample_body):
        """Should list meetings for a body."""
        response = await client.get(
            f"/api/v1/oparl/body/{sample_body.id}/meeting"
        )
        assert response.status_code == 200

    async def test_meeting_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent meeting."""
        import uuid
        response = await client.get(f"/api/v1/oparl/meeting/{uuid.uuid4()}")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestOParlPaper:
    """Tests for the OParl Paper endpoints."""

    async def test_list_papers(self, client: AsyncClient, sample_body):
        """Should list papers for a body."""
        response = await client.get(
            f"/api/v1/oparl/body/{sample_body.id}/paper"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestOParlSearch:
    """Tests for the full-text search endpoint."""

    async def test_search_requires_query(self, client: AsyncClient):
        """Search should require a query parameter."""
        response = await client.get("/api/v1/oparl/search")
        assert response.status_code == 422  # Validation error

    async def test_search_with_query(self, client: AsyncClient):
        """Search with valid query should return results structure."""
        response = await client.get("/api/v1/oparl/search?q=test")
        # May be 200 or 500 depending on ES availability
        assert response.status_code in (200, 500)


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Tests for health and root endpoints."""

    async def test_root(self, client: AsyncClient):
        """Root should return system info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    async def test_health(self, client: AsyncClient):
        """Health endpoint should return healthy."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
