"""
aitema|RIS - Meeting Tests
Tests for meeting-specific business logic.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oparl import AgendaItem, Location, Meeting, Organization


@pytest_asyncio.fixture
async def sample_meeting(db_session: AsyncSession, sample_body):
    """Create a sample meeting with agenda items."""
    location = Location(
        oparl_type="https://schema.oparl.org/1.1/Location",
        description="Rathaus Teststadt",
        street_address="Rathausplatz 1",
        postal_code="12345",
        locality="Teststadt",
        room="Grosser Sitzungssaal",
    )
    db_session.add(location)
    await db_session.flush()

    meeting = Meeting(
        oparl_type="https://schema.oparl.org/1.1/Meeting",
        body_id=sample_body.id,
        location_id=location.id,
        name="42. Sitzung des Rates",
        meeting_state="eingeladen",
        cancelled=False,
        start=datetime(2026, 3, 15, 17, 0, tzinfo=timezone.utc),
        end=datetime(2026, 3, 15, 20, 0, tzinfo=timezone.utc),
    )
    db_session.add(meeting)
    await db_session.flush()

    # Add agenda items
    items = [
        AgendaItem(
            oparl_type="https://schema.oparl.org/1.1/AgendaItem",
            meeting_id=meeting.id,
            number="1",
            name="Eroeffnung und Begruessung",
            public=True,
            order=1,
        ),
        AgendaItem(
            oparl_type="https://schema.oparl.org/1.1/AgendaItem",
            meeting_id=meeting.id,
            number="2",
            name="Genehmigung der Tagesordnung",
            public=True,
            order=2,
        ),
        AgendaItem(
            oparl_type="https://schema.oparl.org/1.1/AgendaItem",
            meeting_id=meeting.id,
            number="3",
            name="Haushaltsentwurf 2026",
            public=True,
            order=3,
        ),
        AgendaItem(
            oparl_type="https://schema.oparl.org/1.1/AgendaItem",
            meeting_id=meeting.id,
            number="4",
            name="Personalangelegenheiten",
            public=False,
            order=4,
        ),
    ]
    for item in items:
        db_session.add(item)
    await db_session.flush()

    return meeting


@pytest.mark.asyncio
class TestMeetingAPI:
    """Tests for meeting-related API endpoints."""

    async def test_get_meeting_with_details(
        self, client: AsyncClient, sample_meeting
    ):
        """Meeting should include all OParl properties."""
        response = await client.get(
            f"/api/v1/oparl/meeting/{sample_meeting.id}"
        )
        assert response.status_code == 200
        data = response.json()

        assert data["type"] == "https://schema.oparl.org/1.1/Meeting"
        assert data["name"] == "42. Sitzung des Rates"
        assert data["meetingState"] == "eingeladen"
        assert data["cancelled"] is False
        assert data["start"] is not None
        assert data["end"] is not None
        assert data["location"] is not None

    async def test_meeting_has_agenda_items(
        self, client: AsyncClient, sample_meeting
    ):
        """Meeting should reference its agenda items."""
        response = await client.get(
            f"/api/v1/oparl/meeting/{sample_meeting.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "agendaItem" in data
        assert len(data["agendaItem"]) == 4

    async def test_list_agenda_items(
        self, client: AsyncClient, sample_meeting
    ):
        """Should list agenda items for a meeting."""
        response = await client.get(
            f"/api/v1/oparl/meeting/{sample_meeting.id}/agenda-item"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 4

    async def test_agenda_item_public_flag(
        self, client: AsyncClient, sample_meeting
    ):
        """Agenda items should have correct public/non-public flags."""
        response = await client.get(
            f"/api/v1/oparl/meeting/{sample_meeting.id}/agenda-item"
        )
        data = response.json()
        items = data["data"]
        # Item 4 (Personalangelegenheiten) should be non-public
        non_public = [i for i in items if i.get("public") is False]
        assert len(non_public) >= 1

    async def test_meetings_list_for_body(
        self, client: AsyncClient, sample_body, sample_meeting
    ):
        """Body meeting list should include the sample meeting."""
        response = await client.get(
            f"/api/v1/oparl/body/{sample_body.id}/meeting"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["totalElements"] >= 1
