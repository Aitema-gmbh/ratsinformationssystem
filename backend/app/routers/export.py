"""
Export API Router for aitema|Rats

Provides calendar (iCal) and PDF export endpoints.
"""
import subprocess
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.oparl import Meeting, Paper, Body
from app.services.calendar import generate_ical_feed
from app.services.pdf_export import (
    generate_tagesordnung_pdf,
    generate_vorlage_pdf,
    generate_sitzungsprotokoll_pdf,
)

router = APIRouter(prefix="/export", tags=["Export"])

# Default tenant for single-tenant setups
DEFAULT_TENANT = os.getenv("DEFAULT_TENANT_ID", "default")


def _get_base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _html_to_pdf(html: str) -> bytes:
    """Convert HTML to PDF using wkhtmltopdf."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f_in:
        f_in.write(html.encode("utf-8"))
        f_in.flush()
        pdf_path = f_in.name.replace(".html", ".pdf")

    try:
        result = subprocess.run(
            ["wkhtmltopdf", "--quiet", "--encoding", "utf-8",
             "--page-size", "A4", "--margin-top", "15mm",
             "--margin-bottom", "20mm", "--margin-left", "15mm",
             "--margin-right", "15mm", f_in.name, pdf_path],
            capture_output=True, timeout=30,
        )
        if result.returncode != 0 and not os.path.exists(pdf_path):
            raise HTTPException(500, "PDF-Generierung fehlgeschlagen")

        with open(pdf_path, "rb") as f_out:
            return f_out.read()
    except FileNotFoundError:
        raise HTTPException(500, "wkhtmltopdf nicht installiert")
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "PDF-Generierung Timeout")
    finally:
        for path in [f_in.name, pdf_path]:
            try:
                os.unlink(path)
            except OSError:
                pass


def _load_meeting(meeting_id: str, db: Session) -> Meeting:
    meeting = (
        db.query(Meeting)
        .options(
            joinedload(Meeting.organization),
            joinedload(Meeting.location),
            joinedload(Meeting.agenda_items).joinedload("consultation").joinedload("paper"),
            joinedload(Meeting.participants),
        )
        .filter(Meeting.id == meeting_id, Meeting.deleted == False)
        .first()
    )
    if not meeting:
        raise HTTPException(404, "Sitzung nicht gefunden")
    return meeting


def _load_paper(paper_id: str, db: Session) -> Paper:
    paper = (
        db.query(Paper)
        .options(
            joinedload(Paper.main_file),
            joinedload(Paper.consultations).joinedload("organization"),
            joinedload(Paper.consultations).joinedload("agenda_item"),
            joinedload(Paper.originator_persons),
            joinedload(Paper.originator_organizations),
        )
        .filter(Paper.id == paper_id, Paper.deleted == False)
        .first()
    )
    if not paper:
        raise HTTPException(404, "Vorlage nicht gefunden")
    return paper


@router.get("/calendar/{body_id}.ics")
def export_calendar(
    body_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Export iCal feed for all meetings of a body."""
    base_url = _get_base_url(request)
    ical = generate_ical_feed(body_id, DEFAULT_TENANT, db, base_url)
    return Response(
        content=ical,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{body_id}.ics"',
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.get("/meeting/{meeting_id}/tagesordnung.pdf")
def export_tagesordnung(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Export meeting agenda as PDF."""
    meeting = _load_meeting(meeting_id, db)
    html = generate_tagesordnung_pdf(meeting)
    pdf_bytes = _html_to_pdf(html)
    filename = f"Tagesordnung_{meeting.name or meeting_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/paper/{paper_id}/vorlage.pdf")
def export_vorlage(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Export paper/Vorlage as PDF."""
    paper = _load_paper(paper_id, db)
    html = generate_vorlage_pdf(paper)
    pdf_bytes = _html_to_pdf(html)
    filename = f"Vorlage_{paper.reference or paper_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/meeting/{meeting_id}/protokoll.pdf")
def export_protokoll(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Export meeting protocol as PDF."""
    meeting = _load_meeting(meeting_id, db)
    html = generate_sitzungsprotokoll_pdf(meeting)
    pdf_bytes = _html_to_pdf(html)
    filename = f"Protokoll_{meeting.name or meeting_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
