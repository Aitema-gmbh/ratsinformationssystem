"""
iCal Calendar Export Service for aitema|Rats

Generates iCalendar (RFC 5545) feeds and single events
for meetings without external dependencies.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.oparl import Meeting, AgendaItem, Body, Organization, Location


def _escape_ical(text: str) -> str:
    """Escape special characters for iCalendar text values."""
    if not text:
        return ""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def _format_dt(dt: Optional[datetime]) -> str:
    """Format datetime to iCalendar DTSTART/DTEND format (UTC)."""
    if not dt:
        return ""
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _fold_line(line: str) -> str:
    """Fold long lines per RFC 5545 (max 75 octets per line)."""
    if len(line.encode("utf-8")) <= 75:
        return line
    result = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            result.append(current)
            current = " " + char
        else:
            current += char
    if current:
        result.append(current)
    return "\r\n".join(result)


def _build_agenda_description(agenda_items: List[AgendaItem]) -> str:
    """Build a text description from agenda items."""
    if not agenda_items:
        return ""
    lines = ["Tagesordnung:", ""]
    for item in sorted(agenda_items, key=lambda a: a.order):
        number = item.number or str(item.order)
        name = item.name or "Ohne Titel"
        public_marker = "" if item.public else " [nichtoeffentlich]"
        lines.append(f"TOP {number}: {name}{public_marker}")
        if item.consultation and item.consultation.paper:
            lines.append(f"  Vorlage: {item.consultation.paper.reference or item.consultation.paper.name}")
    return "\\n".join(lines)


def generate_single_event(
    meeting: Meeting,
    base_url: str = "",
) -> str:
    """Generate a single VEVENT block for a meeting."""
    uid = f"{meeting.id}@aitema-rats"
    summary = meeting.name or "Sitzung"

    # Build location string
    location_parts = []
    if meeting.location:
        loc = meeting.location
        if loc.description:
            location_parts.append(loc.description)
        if loc.room:
            location_parts.append(f"Raum: {loc.room}")
        if loc.street_address:
            location_parts.append(loc.street_address)
        if loc.locality:
            if loc.postal_code:
                location_parts.append(f"{loc.postal_code} {loc.locality}")
            else:
                location_parts.append(loc.locality)
    location = ", ".join(location_parts)

    # Build description from agenda items
    description = _build_agenda_description(list(meeting.agenda_items))
    if meeting.cancelled:
        description = "ABGESAGT\\n\\n" + description

    # Start and end times
    dtstart = _format_dt(meeting.start)
    dtend = _format_dt(meeting.end)
    if not dtend and meeting.start:
        dtend = _format_dt(meeting.start + timedelta(hours=2))

    # Organization / category
    categories = ""
    if meeting.organization:
        categories = meeting.organization.organization_type or ""

    # URL to meeting detail
    url = f"{base_url}/sitzungen/{meeting.id}" if base_url else ""

    # Timestamp for DTSTAMP
    dtstamp = _format_dt(datetime.utcnow())

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
    ]

    if dtstart:
        lines.append(f"DTSTART:{dtstart}")
    if dtend:
        lines.append(f"DTEND:{dtend}")

    lines.append(f"SUMMARY:{_escape_ical(summary)}")

    if location:
        lines.append(f"LOCATION:{_escape_ical(location)}")
    if description:
        lines.append(f"DESCRIPTION:{description}")
    if url:
        lines.append(f"URL:{url}")
    if categories:
        lines.append(f"CATEGORIES:{_escape_ical(categories)}")

    if meeting.cancelled:
        lines.append("STATUS:CANCELLED")
    elif meeting.meeting_state == "completed":
        lines.append("STATUS:CONFIRMED")
    else:
        lines.append("STATUS:TENTATIVE")

    if meeting.modified:
        lines.append(f"LAST-MODIFIED:{_format_dt(meeting.modified)}")

    lines.append("END:VEVENT")

    return "\r\n".join(_fold_line(line) for line in lines)


def generate_ical_feed(
    body_id: str,
    tenant_id: str,
    db: Session,
    base_url: str = "",
) -> str:
    """
    Generate a complete iCalendar feed for all meetings of a body.

    Args:
        body_id: The Body UUID to filter meetings
        tenant_id: Tenant ID for multi-tenant isolation
        db: SQLAlchemy session
        base_url: Base URL for links in events

    Returns:
        Complete iCalendar string (RFC 5545)
    """
    body = db.query(Body).filter(
        Body.id == body_id,
        Body.tenant_id == tenant_id,
        Body.deleted == False,
    ).first()

    cal_name = body.name if body else "aitema|Rats Sitzungskalender"

    meetings = db.query(Meeting).filter(
        Meeting.body_id == body_id,
        Meeting.deleted == False,
    ).order_by(Meeting.start.desc()).limit(500).all()

    # Build VCALENDAR
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//aitema GmbH//aitema|Rats//DE",
        f"X-WR-CALNAME:{_escape_ical(cal_name)}",
        "X-WR-TIMEZONE:Europe/Berlin",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for meeting in meetings:
        lines.append(generate_single_event(meeting, base_url))

    lines.append("END:VCALENDAR")

    return "\r\n".join(lines)
