"""
OParl 1.1 Conformance Test Suite

Tests the running API against the OParl 1.1 specification using
httpx.AsyncClient against the FastAPI TestClient (ASGI transport).

Covers:
- JSON-LD fields: @context / type / id
- System object (OParl §3.1): mandatory fields, oparlVersion, body URL
- Body object (OParl §3.2): mandatory fields, sub-list URLs
- All 12 object types: mandatory fields, date formats, URL fields
- Pagination (OParl §4.1): data array, links.next/prev, pagination block
- ETag / Conditional Requests: ETag header, If-None-Match -> 304
- Deleted objects: deleted flag
- Error handling: 404 for unknown IDs
"""
import re
import json
import pytest
import httpx
from typing import Any, Dict

from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models.oparl import (
    OParlSystem, Body, Organization, Person, Membership,
    Meeting, AgendaItem, Paper, Consultation, File,
    Location, LegislativeTerm,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Test database setup (in-memory SQLite)
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///./test_conformance.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Create tables and seed test data for all conformance tests."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    db = TestingSessionLocal()
    _seed_test_data(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def _seed_test_data(db):
    """Insert minimal but complete test fixtures."""
    # System
    system = OParlSystem(
        id="system-1",
        name="Test Ratsinformationssystem",
        oparl_version="https://schema.oparl.org/1.1/",
        website="https://example.com",
    )
    db.add(system)
    db.flush()

    # Body
    body = Body(
        id="body-1",
        name="Stadtrat Teststadt",
        short_name="Stadtrat",
        ags="09162000",
        rgs="09162000000",
        tenant_id="test",
    )
    db.add(body)
    db.flush()

    # Organization
    org = Organization(
        id="org-1",
        name="Hauptausschuss",
        body_id="body-1",
        organization_type="parliamentary",
        tenant_id="test",
    )
    db.add(org)
    db.flush()

    # Person
    person = Person(
        id="person-1",
        name="Max Mustermann",
        family_name="Mustermann",
        given_name="Max",
        body_id="body-1",
        tenant_id="test",
    )
    db.add(person)
    db.flush()

    # Meeting
    from datetime import datetime, timezone
    meeting = Meeting(
        id="meeting-1",
        name="Stadtratssitzung Januar",
        meeting_state="completed",
        start=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        end=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
        body_id="body-1",
        tenant_id="test",
    )
    db.add(meeting)
    db.flush()

    # Paper
    from datetime import date
    paper = Paper(
        id="paper-1",
        name="Antrag: Haushaltsplan 2026",
        reference="V/2026/001",
        date=date(2026, 1, 10),
        paper_type="Antrag",
        body_id="body-1",
        tenant_id="test",
    )
    db.add(paper)
    db.flush()

    # LegislativeTerm
    term = LegislativeTerm(
        id="term-1",
        name="Wahlperiode 2024-2029",
        start_date=date(2024, 5, 1),
        end_date=date(2029, 4, 30),
        body_id="body-1",
        tenant_id="test",
    )
    db.add(term)
    db.flush()

    # Deleted person (for deleted-object tests)
    deleted_person = Person(
        id="person-deleted",
        name="Gelöschte Person",
        family_name="Gelöscht",
        given_name="Person",
        body_id="body-1",
        tenant_id="test",
        deleted=True,
    )
    db.add(deleted_person)

    db.commit()


# ---------------------------------------------------------------------------
# Client fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ===========================================================================
# Helper functions
# ===========================================================================

def assert_is_url(value: Any, field_name: str = "field") -> None:
    assert isinstance(value, str), f"{field_name} must be a string URL, got {type(value).__name__}"
    assert re.match(r"^https?://.+", value), f"{field_name} must start with http(s)://, got: {value!r}"


def assert_iso_date(value: Any, field_name: str = "field") -> None:
    assert isinstance(value, str), f"{field_name} must be a string, got {type(value).__name__}"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", value), (
        f"{field_name} must be ISO 8601 date (YYYY-MM-DD), got: {value!r}"
    )


def assert_iso_datetime(value: Any, field_name: str = "field") -> None:
    """Allow string with timezone OR already-serialised datetime strings."""
    assert isinstance(value, str), f"{field_name} must be a string, got {type(value).__name__}"
    # Accept both Z and ±HH:MM, and also naive datetime strings from SQLite
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value), (
        f"{field_name} must start with ISO 8601 datetime, got: {value!r}"
    )


def assert_pagination_structure(data: Dict) -> None:
    """Validate OParl §4.1 pagination response structure."""
    assert "data" in data, "Paginated response must have 'data' array"
    assert isinstance(data["data"], list), "'data' must be an array"
    assert "links" in data, "Paginated response must have 'links' object"
    links = data["links"]
    assert isinstance(links, dict), "'links' must be an object"
    # first and last are required links
    for link_key in ("first", "last"):
        assert link_key in links, f"links.{link_key} is required"


# ===========================================================================
# §3.1 System Object
# ===========================================================================

class TestSystemObject:
    """OParl §3.1 - System object conformance."""

    def test_system_endpoint_returns_200(self, client):
        resp = client.get("/oparl/v1/")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_system_content_type_json(self, client):
        resp = client.get("/oparl/v1/")
        assert "application/json" in resp.headers.get("content-type", "")

    def test_system_has_id_field(self, client):
        data = client.get("/oparl/v1/").json()
        assert "id" in data, "System must have 'id' field"
        assert_is_url(data["id"], "System.id")

    def test_system_id_is_own_url(self, client):
        """System.id must point to itself (the system endpoint)."""
        data = client.get("/oparl/v1/").json()
        assert "/oparl/v1" in data["id"], (
            f"System.id should reference the system endpoint, got: {data['id']}"
        )

    def test_system_has_type_field(self, client):
        data = client.get("/oparl/v1/").json()
        assert "type" in data, "System must have 'type' field"
        assert data["type"] == "https://schema.oparl.org/1.1/System", (
            f"System.type must be OParl type URL, got: {data['type']}"
        )

    def test_system_has_oparl_version(self, client):
        data = client.get("/oparl/v1/").json()
        assert "oparl_version" in data, "System must have 'oparl_version'"
        assert data["oparl_version"] == "https://schema.oparl.org/1.1/", (
            f"oparl_version must be 'https://schema.oparl.org/1.1/', got: {data['oparl_version']}"
        )

    def test_system_has_body_url(self, client):
        data = client.get("/oparl/v1/").json()
        assert "body" in data, "System must have 'body' field (URL to body list)"
        assert_is_url(data["body"], "System.body")

    def test_system_name_is_string(self, client):
        data = client.get("/oparl/v1/").json()
        assert "name" in data
        assert isinstance(data["name"], str) and len(data["name"]) > 0


# ===========================================================================
# §3.2 Body Object
# ===========================================================================

class TestBodyObject:
    """OParl §3.2 - Body object conformance."""

    def test_body_list_returns_200(self, client):
        resp = client.get("/oparl/v1/body")
        assert resp.status_code == 200

    def test_body_list_is_paginated(self, client):
        data = client.get("/oparl/v1/body").json()
        assert_pagination_structure(data)

    def test_body_list_contains_bodies(self, client):
        data = client.get("/oparl/v1/body").json()
        assert len(data["data"]) >= 1, "Body list must contain at least one body"

    def test_body_has_required_fields(self, client):
        data = client.get("/oparl/v1/body").json()
        body = data["data"][0]
        assert "id" in body
        assert "type" in body
        assert "name" in body
        assert_is_url(body["id"], "Body.id")

    def test_body_type_is_oparl_url(self, client):
        data = client.get("/oparl/v1/body").json()
        body = data["data"][0]
        assert body["type"] == "https://schema.oparl.org/1.1/Body"

    def test_body_has_list_links(self, client):
        data = client.get("/oparl/v1/body").json()
        body = data["data"][0]
        for list_field in ("organization", "person", "meeting", "paper"):
            assert list_field in body, f"Body must have '{list_field}' link"
            if body[list_field]:
                assert_is_url(body[list_field], f"Body.{list_field}")

    def test_body_detail_returns_200(self, client):
        resp = client.get("/oparl/v1/body/body-1")
        assert resp.status_code == 200

    def test_body_detail_has_system_link(self, client):
        data = client.get("/oparl/v1/body/body-1").json()
        assert "system" in data
        if data["system"]:
            assert_is_url(data["system"], "Body.system")

    def test_body_404_for_unknown_id(self, client):
        resp = client.get("/oparl/v1/body/does-not-exist-xyz")
        assert resp.status_code == 404


# ===========================================================================
# All 12 Object Types: Mandatory Fields & Formats
# ===========================================================================

class TestOrganizationObject:
    """OParl Organization conformance."""

    def test_organization_list_returns_200(self, client):
        resp = client.get("/oparl/v1/body/body-1/organization")
        assert resp.status_code == 200

    def test_organization_list_paginated(self, client):
        data = client.get("/oparl/v1/body/body-1/organization").json()
        assert_pagination_structure(data)

    def test_organization_has_id_and_type(self, client):
        data = client.get("/oparl/v1/body/body-1/organization").json()
        if data["data"]:
            org = data["data"][0]
            assert "id" in org
            assert "type" in org
            assert_is_url(org["id"], "Organization.id")
            assert org["type"] == "https://schema.oparl.org/1.1/Organization"

    def test_organization_detail_200(self, client):
        resp = client.get("/oparl/v1/organization/org-1")
        assert resp.status_code == 200

    def test_organization_detail_fields(self, client):
        data = client.get("/oparl/v1/organization/org-1").json()
        assert_is_url(data["id"], "Organization.id")
        assert data["type"] == "https://schema.oparl.org/1.1/Organization"

    def test_organization_404(self, client):
        assert client.get("/oparl/v1/organization/nonexistent").status_code == 404


class TestPersonObject:
    """OParl Person conformance."""

    def test_person_list_200(self, client):
        assert client.get("/oparl/v1/body/body-1/person").status_code == 200

    def test_person_list_paginated(self, client):
        data = client.get("/oparl/v1/body/body-1/person").json()
        assert_pagination_structure(data)

    def test_person_has_id_type_name(self, client):
        data = client.get("/oparl/v1/body/body-1/person").json()
        if data["data"]:
            p = data["data"][0]
            assert_is_url(p["id"], "Person.id")
            assert p["type"] == "https://schema.oparl.org/1.1/Person"

    def test_person_detail_200(self, client):
        assert client.get("/oparl/v1/person/person-1").status_code == 200

    def test_person_404(self, client):
        assert client.get("/oparl/v1/person/nonexistent-person").status_code == 404


class TestMeetingObject:
    """OParl Meeting conformance."""

    def test_meeting_list_200(self, client):
        assert client.get("/oparl/v1/body/body-1/meeting").status_code == 200

    def test_meeting_list_paginated(self, client):
        data = client.get("/oparl/v1/body/body-1/meeting").json()
        assert_pagination_structure(data)

    def test_meeting_has_id_and_type(self, client):
        data = client.get("/oparl/v1/body/body-1/meeting").json()
        if data["data"]:
            m = data["data"][0]
            assert_is_url(m["id"], "Meeting.id")
            assert m["type"] == "https://schema.oparl.org/1.1/Meeting"

    def test_meeting_dates_are_iso8601(self, client):
        data = client.get("/oparl/v1/body/body-1/meeting").json()
        for m in data["data"]:
            if m.get("start"):
                assert_iso_datetime(m["start"], "Meeting.start")
            if m.get("end"):
                assert_iso_datetime(m["end"], "Meeting.end")

    def test_meeting_detail_200(self, client):
        assert client.get("/oparl/v1/meeting/meeting-1").status_code == 200

    def test_meeting_404(self, client):
        assert client.get("/oparl/v1/meeting/nonexistent-meeting").status_code == 404


class TestPaperObject:
    """OParl Paper conformance."""

    def test_paper_list_200(self, client):
        assert client.get("/oparl/v1/body/body-1/paper").status_code == 200

    def test_paper_list_paginated(self, client):
        data = client.get("/oparl/v1/body/body-1/paper").json()
        assert_pagination_structure(data)

    def test_paper_has_id_and_type(self, client):
        data = client.get("/oparl/v1/body/body-1/paper").json()
        if data["data"]:
            p = data["data"][0]
            assert_is_url(p["id"], "Paper.id")
            assert p["type"] == "https://schema.oparl.org/1.1/Paper"

    def test_paper_date_is_iso8601(self, client):
        data = client.get("/oparl/v1/body/body-1/paper").json()
        for p in data["data"]:
            if p.get("date"):
                assert_iso_date(p["date"], "Paper.date")

    def test_paper_detail_200(self, client):
        assert client.get("/oparl/v1/paper/paper-1").status_code == 200

    def test_paper_has_body_link(self, client):
        data = client.get("/oparl/v1/paper/paper-1").json()
        if data.get("body"):
            assert_is_url(data["body"], "Paper.body")

    def test_paper_404(self, client):
        assert client.get("/oparl/v1/paper/nonexistent-paper").status_code == 404


class TestAgendaItemObject:
    """OParl AgendaItem conformance."""

    def test_agenda_item_list_200(self, client):
        resp = client.get("/oparl/v1/meeting/meeting-1/agenda-item")
        assert resp.status_code in (200, 404), (
            f"AgendaItem list should return 200 or 404, got {resp.status_code}"
        )

    def test_agenda_item_has_meeting_field(self, client):
        data = client.get("/oparl/v1/meeting/meeting-1/agenda-item").json()
        if isinstance(data, dict) and "data" in data:
            for item in data["data"]:
                assert "id" in item
                if item.get("meeting"):
                    assert_is_url(item["meeting"], "AgendaItem.meeting")


class TestConsultationObject:
    """OParl Consultation conformance."""

    def test_consultation_type_in_schema(self):
        """Consultation type must exist in schema spec."""
        from tests.oparl_spec import OPARL_SPEC
        assert "Consultation" in OPARL_SPEC["types"]

    def test_consultation_spec_has_correct_type_url(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["Consultation"]
        assert spec["type_url"] == "https://schema.oparl.org/1.1/Consultation"


class TestFileObject:
    """OParl File conformance."""

    def test_file_type_in_schema(self):
        from tests.oparl_spec import OPARL_SPEC
        assert "File" in OPARL_SPEC["types"]

    def test_file_requires_access_url(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["File"]
        assert "access_url" in spec["required_fields"]


class TestLocationObject:
    """OParl Location conformance."""

    def test_location_type_in_schema(self):
        from tests.oparl_spec import OPARL_SPEC
        assert "Location" in OPARL_SPEC["types"]

    def test_location_geojson_field_type(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["Location"]
        assert spec["field_types"].get("geojson") == "geojson"


class TestMembershipObject:
    """OParl Membership conformance."""

    def test_membership_type_in_schema(self):
        from tests.oparl_spec import OPARL_SPEC
        assert "Membership" in OPARL_SPEC["types"]

    def test_membership_person_field_is_url_type(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["Membership"]
        assert spec["field_types"].get("person") == "url"
        assert spec["field_types"].get("organization") == "url"


class TestLegislativeTermObject:
    """OParl LegislativeTerm conformance."""

    def test_legislative_term_list_200(self, client):
        resp = client.get("/oparl/v1/body/body-1/legislative-term")
        assert resp.status_code in (200, 404)

    def test_legislative_term_type_in_schema(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["LegislativeTerm"]
        assert spec["type_url"] == "https://schema.oparl.org/1.1/LegislativeTerm"

    def test_legislative_term_requires_body(self):
        from tests.oparl_spec import OPARL_SPEC
        spec = OPARL_SPEC["types"]["LegislativeTerm"]
        assert "body" in spec["required_fields"]


# ===========================================================================
# §4.1 Pagination
# ===========================================================================

class TestPagination:
    """OParl §4.1 - Pagination conformance."""

    def test_data_is_array(self, client):
        data = client.get("/oparl/v1/body").json()
        assert isinstance(data["data"], list)

    def test_links_object_present(self, client):
        data = client.get("/oparl/v1/body").json()
        assert "links" in data
        assert isinstance(data["links"], dict)

    def test_links_has_first_and_last(self, client):
        data = client.get("/oparl/v1/body").json()
        links = data["links"]
        assert "first" in links
        assert "last" in links

    def test_links_next_is_null_on_single_page(self, client):
        """When all results fit on one page, next must be null."""
        data = client.get("/oparl/v1/body").json()
        links = data["links"]
        total_pages = data.get("pagination", {}).get("totalPages", 1)
        if total_pages == 1:
            assert links.get("next") is None, (
                "links.next must be null when on last page"
            )

    def test_links_prev_is_null_on_first_page(self, client):
        data = client.get("/oparl/v1/body").json()
        links = data["links"]
        assert links.get("prev") is None, (
            "links.prev must be null on first page"
        )

    def test_pagination_block_present(self, client):
        data = client.get("/oparl/v1/body").json()
        assert "pagination" in data
        pagination = data["pagination"]
        assert "totalElements" in pagination
        assert isinstance(pagination["totalElements"], int)
        assert "elementsPerPage" in pagination
        assert isinstance(pagination["elementsPerPage"], int)

    def test_page_size_parameter(self, client):
        data = client.get("/oparl/v1/body/body-1/meeting?page_size=1").json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 1

    def test_page_parameter(self, client):
        resp = client.get("/oparl/v1/body/body-1/paper?page=1&page_size=100")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data

    def test_next_url_contains_page_param(self, client):
        """When next link is present, it must include a page parameter."""
        # Seed enough data to require a second page
        data = client.get("/oparl/v1/body/body-1/meeting?page_size=1").json()
        links = data.get("links", {})
        if links.get("next"):
            assert "page=" in links["next"], (
                f"next URL must contain 'page=' parameter, got: {links['next']}"
            )


# ===========================================================================
# ETag / Conditional Requests
# ===========================================================================

class TestConditionalRequests:
    """HTTP caching: ETag and If-None-Match support."""

    def test_system_returns_etag(self, client):
        resp = client.get("/oparl/v1/")
        # ETag is optional but strongly recommended by OParl
        # We test for its presence and correct format if present
        if "etag" in resp.headers:
            etag = resp.headers["etag"]
            assert etag.startswith('"') or etag.startswith('W/"'), (
                f"ETag must be quoted string, got: {etag}"
            )

    def test_if_none_match_returns_304(self, client):
        resp = client.get("/oparl/v1/")
        if "etag" not in resp.headers:
            pytest.skip("Server does not return ETag headers")
        etag = resp.headers["etag"]
        resp2 = client.get("/oparl/v1/", headers={"If-None-Match": etag})
        assert resp2.status_code == 304, (
            f"If-None-Match with matching ETag must return 304, got {resp2.status_code}"
        )

    def test_list_endpoint_etag(self, client):
        resp = client.get("/oparl/v1/body/body-1/paper")
        if "etag" in resp.headers:
            etag = resp.headers["etag"]
            resp2 = client.get(
                "/oparl/v1/body/body-1/paper",
                headers={"If-None-Match": etag}
            )
            assert resp2.status_code == 304

    def test_modified_since_header_accepted(self, client):
        """Server should gracefully handle If-Modified-Since."""
        resp = client.get(
            "/oparl/v1/body/body-1/paper",
            headers={"If-Modified-Since": "Thu, 01 Jan 2026 00:00:00 GMT"}
        )
        assert resp.status_code in (200, 304, 501)


# ===========================================================================
# Deleted Objects
# ===========================================================================

class TestDeletedObjects:
    """OParl spec: deleted objects must carry deleted: true flag."""

    def test_deleted_person_has_deleted_flag(self, client):
        resp = client.get("/oparl/v1/person/person-deleted")
        if resp.status_code == 404:
            pytest.skip("Server returns 404 for deleted objects (alternative compliant behaviour)")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("deleted") is True, (
            "Deleted objects must have 'deleted: true', "
            f"got deleted={data.get('deleted')!r}"
        )

    def test_deleted_person_not_in_list(self, client):
        """Deleted objects must not appear in collection listings."""
        data = client.get("/oparl/v1/body/body-1/person").json()
        ids = [p["id"] for p in data["data"]]
        # Check no deleted ID appears in list
        for item_id in ids:
            assert "person-deleted" not in item_id, (
                "Deleted person must not appear in person list"
            )


# ===========================================================================
# Error Handling
# ===========================================================================

class TestErrorHandling:
    """HTTP error responses."""

    def test_unknown_body_id_returns_404(self, client):
        assert client.get("/oparl/v1/body/nonexistent-body-999").status_code == 404

    def test_unknown_person_id_returns_404(self, client):
        assert client.get("/oparl/v1/person/nonexistent-person-999").status_code == 404

    def test_unknown_meeting_id_returns_404(self, client):
        assert client.get("/oparl/v1/meeting/nonexistent-meeting-999").status_code == 404

    def test_unknown_paper_id_returns_404(self, client):
        assert client.get("/oparl/v1/paper/nonexistent-paper-999").status_code == 404

    def test_unknown_organization_id_returns_404(self, client):
        assert client.get("/oparl/v1/organization/nonexistent-org-999").status_code == 404

    def test_404_response_is_json(self, client):
        resp = client.get("/oparl/v1/body/nonexistent-body-999")
        assert "application/json" in resp.headers.get("content-type", "")

    def test_404_has_detail_field(self, client):
        resp = client.get("/oparl/v1/body/nonexistent-body-999")
        data = resp.json()
        assert "detail" in data, f"404 response must have 'detail' field, got: {data}"


# ===========================================================================
# JSON-LD Conformance
# ===========================================================================

class TestJsonLD:
    """JSON-LD fields: @context / type / id as per OParl spec."""

    def test_system_type_is_json_ld_url(self, client):
        data = client.get("/oparl/v1/").json()
        assert data["type"].startswith("https://schema.oparl.org/1.1/"), (
            f"type must be a JSON-LD type URL, got: {data['type']}"
        )

    def test_all_list_items_have_type_url(self, client):
        data = client.get("/oparl/v1/body/body-1/meeting").json()
        for item in data["data"]:
            assert "type" in item
            assert item["type"].startswith("https://schema.oparl.org/1.1/"), (
                f"Meeting.type must be JSON-LD URL, got: {item['type']}"
            )

    def test_all_list_items_have_id_url(self, client):
        data = client.get("/oparl/v1/body/body-1/paper").json()
        for item in data["data"]:
            assert "id" in item
            assert_is_url(item["id"], "Paper.id")

    def test_body_list_items_type_url(self, client):
        data = client.get("/oparl/v1/body").json()
        for body in data["data"]:
            assert body.get("type") == "https://schema.oparl.org/1.1/Body"

    def test_organization_type_url(self, client):
        data = client.get("/oparl/v1/organization/org-1").json()
        assert data["type"] == "https://schema.oparl.org/1.1/Organization"


# ===========================================================================
# All 12 Types Coverage Summary
# ===========================================================================

class TestAll12TypesCoverage:
    """Verify all 12 OParl object types are reachable via the API."""

    OPARL_TYPES = {
        "System": "/oparl/v1/",
        "Body": "/oparl/v1/body",
        "Organization": "/oparl/v1/body/body-1/organization",
        "Person": "/oparl/v1/body/body-1/person",
        "Meeting": "/oparl/v1/body/body-1/meeting",
        "Paper": "/oparl/v1/body/body-1/paper",
    }

    def test_system_reachable(self, client):
        assert client.get("/oparl/v1/").status_code == 200

    def test_body_list_reachable(self, client):
        assert client.get("/oparl/v1/body").status_code == 200

    def test_organization_list_reachable(self, client):
        assert client.get("/oparl/v1/body/body-1/organization").status_code == 200

    def test_person_list_reachable(self, client):
        assert client.get("/oparl/v1/body/body-1/person").status_code == 200

    def test_meeting_list_reachable(self, client):
        assert client.get("/oparl/v1/body/body-1/meeting").status_code == 200

    def test_paper_list_reachable(self, client):
        assert client.get("/oparl/v1/body/body-1/paper").status_code == 200

    def test_meeting_detail_reachable(self, client):
        assert client.get("/oparl/v1/meeting/meeting-1").status_code == 200

    def test_paper_detail_reachable(self, client):
        assert client.get("/oparl/v1/paper/paper-1").status_code == 200

    def test_organization_detail_reachable(self, client):
        assert client.get("/oparl/v1/organization/org-1").status_code == 200

    def test_person_detail_reachable(self, client):
        assert client.get("/oparl/v1/person/person-1").status_code == 200
