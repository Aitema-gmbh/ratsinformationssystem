"""
aitema|RIS - ICS Kalender-Export (E4)

Endpoints:
  GET /api/calendar/sitzungen.ics                    – Alle Sitzungen
  GET /api/calendar/gremium/{committee_id}/sitzungen.ics – Gremium-spezifisch
"""
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from icalendar import Calendar, Event
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.oparl import Meeting, Organization, Location

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


def _location_text(meeting: Meeting) -> str | None:
    """Gibt einen lesbaren Ortstext zurück, sofern vorhanden."""
    loc: Location | None = getattr(meeting, "location", None)
    if loc is None:
        return None
    parts = []
    if loc.room:
        parts.append(loc.room)
    if loc.street_address:
        parts.append(loc.street_address)
    if loc.locality:
        parts.append(loc.locality)
    return ", ".join(p for p in parts if p) or loc.description or loc.name or None


def _safe_end(meeting: Meeting) -> datetime:
    """Gibt ein valides dtend zurück (mindestens start + 1 Stunde)."""
    start: datetime | None = meeting.start
    end: datetime | None = meeting.end
    if start is None:
        return datetime.now(timezone.utc) + timedelta(hours=1)
    if end and end > start:
        return end
    return start + timedelta(hours=1)


def build_calendar(meetings: list, title: str = "aitema|RIS Sitzungskalender") -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//aitema|RIS//aitema.de//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", title)
    cal.add("x-wr-timezone", "Europe/Berlin")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    for m in meetings:
        ev = Event()
        # UID: eindeutig pro Sitzung
        ev.add("uid", f"{m.id}@ris.aitema.de")
        ev.add("summary", m.name or "Sitzung")

        # Zeitstempel
        dtstart: datetime = m.start if m.start else datetime.now(timezone.utc)
        if dtstart.tzinfo is None:
            dtstart = dtstart.replace(tzinfo=timezone.utc)
        dtend: datetime = _safe_end(m)
        if dtend.tzinfo is None:
            dtend = dtend.replace(tzinfo=timezone.utc)

        ev.add("dtstart", dtstart)
        ev.add("dtend", dtend)
        ev.add("dtstamp", datetime.now(timezone.utc))

        # Ort
        loc_text = _location_text(m)
        if loc_text:
            ev.add("location", loc_text)

        # Status
        if m.cancelled:
            ev.add("status", "CANCELLED")
        elif m.meeting_state == "completed":
            ev.add("status", "CONFIRMED")
        else:
            ev.add("status", "CONFIRMED")

        ev.add("description", f"Weitere Informationen: https://ris.aitema.de/sitzungen/{m.id}")
        ev.add("url", f"https://ris.aitema.de/sitzungen/{m.id}")
        cal.add_component(ev)

    return cal.to_ical()


@router.get(
    "/sitzungen.ics",
    summary="Alle Sitzungen als ICS-Kalender",
    response_class=Response,
)
def all_meetings_ics(
    tenant_id: str | None = Query(default=None, description="Optional: Mandant filtern"),
    db: Session = Depends(get_db),
):
    """Gibt alle (max. 200) bevorstehenden und vergangenen Sitzungen als ICS zurück."""
    q = db.query(Meeting).filter(Meeting.deleted.is_(False))
    if tenant_id:
        q = q.filter(Meeting.tenant_id == tenant_id)
    meetings = q.order_by(Meeting.start).limit(200).all()
    ics = build_calendar(meetings, "aitema|RIS – Alle Sitzungen")
    return Response(
        content=ics,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=sitzungen.ics"},
    )


@router.get(
    "/gremium/{committee_id}/sitzungen.ics",
    summary="Sitzungen eines Gremiums als ICS-Kalender",
    response_class=Response,
)
def committee_meetings_ics(
    committee_id: str,
    db: Session = Depends(get_db),
):
    """Gibt alle Sitzungen eines bestimmten Gremiums (Organization) als ICS zurück."""
    # Gremiumsname für Kalendertitel laden
    org: Organization | None = db.query(Organization).filter(
        Organization.id == committee_id,
        Organization.deleted.is_(False),
    ).first()
    org_name = org.name if org else "Ausschuss"

    meetings = (
        db.query(Meeting)
        .filter(
            Meeting.organization_id == committee_id,
            Meeting.deleted.is_(False),
        )
        .order_by(Meeting.start)
        .all()
    )
    ics = build_calendar(meetings, f"aitema|RIS – {org_name}")
    return Response(
        content=ics,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=sitzungen-{committee_id}.ics"
        },
    )
