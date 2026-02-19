"""
OParl 1.1 API Router

Implements the OParl JSON API specification for interoperability
with other Ratsinformationssysteme.

All endpoints return OParl-compliant JSON with:
- Proper type URLs
- Pagination (OParl 1.1 style)
- External object list URLs
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.oparl import (
    OParlSystem, Body, Organization, Person, Membership,
    Meeting, AgendaItem, Paper, Consultation, File,
    Location, LegislativeTerm,
)
from app.schemas.oparl import (
    SystemSchema, BodySchema, OrganizationSchema, PersonSchema,
    MembershipSchema, MeetingSchema, AgendaItemSchema, PaperSchema,
    ConsultationSchema, FileSchema, LocationSchema, LegislativeTermSchema,
    PaginatedResponse,
)

router = APIRouter(prefix="/oparl/v1", tags=["OParl 1.1"])

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500


def get_base_url(request: Request) -> str:
    """Get the base URL for building OParl URLs."""
    return str(request.base_url).rstrip('/')


def paginate(query, page: int, page_size: int, base_url: str, path: str):
    """Apply OParl-style pagination to a query."""
    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "data": items,
        "pagination": {
            "totalElements": total,
            "elementsPerPage": page_size,
            "currentPage": page,
            "totalPages": total_pages,
        },
        "links": {
            "first": f"{base_url}{path}?page=1",
            "last": f"{base_url}{path}?page={total_pages}",
            "next": f"{base_url}{path}?page={page + 1}" if page < total_pages else None,
            "prev": f"{base_url}{path}?page={page - 1}" if page > 1 else None,
        }
    }


# ============================================================
# System
# ============================================================
@router.get("/", response_model=SystemSchema)
def get_system(request: Request, db: Session = Depends(get_db)):
    """OParl:System - API entry point."""
    system = db.query(OParlSystem).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not configured")
    
    base = get_base_url(request)
    return SystemSchema(
        id=f"{base}/oparl/v1/",
        name=system.name,
        oparl_version=system.oparl_version,
        website=system.website,
        contact_email=system.contact_email,
        contact_name=system.contact_name,
        vendor=system.vendor,
        product=system.product,
        body=f"{base}/oparl/v1/body",
    )


# ============================================================
# Body
# ============================================================
@router.get("/body")
def list_bodies(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    """OParl:Body - List all Koerperschaften."""
    base = get_base_url(request)
    query = db.query(Body).filter(Body.deleted == False)
    result = paginate(query, page, page_size, base, "/oparl/v1/body")
    
    result["data"] = [
        BodySchema(
            id=f"{base}/oparl/v1/body/{b.id}",
            name=b.name,
            short_name=b.short_name,
            body_type=b.body_type,
            ags=b.ags,
            rgs=b.rgs,
            contact_email=b.contact_email,
            created=b.created,
            modified=b.modified,
            system=f"{base}/oparl/v1/",
            organization=f"{base}/oparl/v1/body/{b.id}/organization",
            person=f"{base}/oparl/v1/body/{b.id}/person",
            meeting=f"{base}/oparl/v1/body/{b.id}/meeting",
            paper=f"{base}/oparl/v1/body/{b.id}/paper",
            legislative_term=f"{base}/oparl/v1/body/{b.id}/legislativeterm",
        )
        for b in result["data"]
    ]
    return result


@router.get("/body/{body_id}", response_model=BodySchema)
def get_body(body_id: str, request: Request, db: Session = Depends(get_db)):
    """Get a single Body."""
    body = db.query(Body).filter(Body.id == body_id, Body.deleted == False).first()
    if not body:
        raise HTTPException(status_code=404, detail="Body not found")
    
    base = get_base_url(request)
    return BodySchema(
        id=f"{base}/oparl/v1/body/{body.id}",
        name=body.name,
        short_name=body.short_name,
        body_type=body.body_type,
        ags=body.ags,
        rgs=body.rgs,
        contact_email=body.contact_email,
        created=body.created,
        modified=body.modified,
        system=f"{base}/oparl/v1/",
        organization=f"{base}/oparl/v1/body/{body.id}/organization",
        person=f"{base}/oparl/v1/body/{body.id}/person",
        meeting=f"{base}/oparl/v1/body/{body.id}/meeting",
        paper=f"{base}/oparl/v1/body/{body.id}/paper",
        legislative_term=f"{base}/oparl/v1/body/{body.id}/legislativeterm",
    )


# ============================================================
# Organization
# ============================================================
@router.get("/body/{body_id}/organization")
def list_organizations(
    body_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    organization_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """OParl:Organization - List Fraktionen, Ausschuesse etc."""
    base = get_base_url(request)
    query = db.query(Organization).filter(
        Organization.body_id == body_id,
        Organization.deleted == False
    )
    if organization_type:
        query = query.filter(Organization.organization_type == organization_type)
    
    result = paginate(query, page, page_size, base, f"/oparl/v1/body/{body_id}/organization")
    result["data"] = [
        OrganizationSchema(
            id=f"{base}/oparl/v1/organization/{o.id}",
            name=o.name,
            short_name=o.short_name,
            body=f"{base}/oparl/v1/body/{body_id}",
            organization_type=o.organization_type,
            classification=o.classification,
            start_date=o.start_date,
            end_date=o.end_date,
            created=o.created,
            modified=o.modified,
        )
        for o in result["data"]
    ]
    return result


@router.get("/organization/{org_id}", response_model=OrganizationSchema)
def get_organization(org_id: str, request: Request, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")
    base = get_base_url(request)
    return OrganizationSchema(
        id=f"{base}/oparl/v1/organization/{org.id}",
        name=org.name, short_name=org.short_name,
        body=f"{base}/oparl/v1/body/{org.body_id}",
        organization_type=org.organization_type,
        classification=org.classification,
        start_date=org.start_date, end_date=org.end_date,
        created=org.created, modified=org.modified,
    )


# ============================================================
# Person
# ============================================================
@router.get("/body/{body_id}/person")
def list_persons(
    body_id: str, request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    base = get_base_url(request)
    query = db.query(Person).filter(Person.body_id == body_id, Person.deleted == False)
    result = paginate(query, page, page_size, base, f"/oparl/v1/body/{body_id}/person")
    result["data"] = [
        PersonSchema(
            id=f"{base}/oparl/v1/person/{p.id}",
            name=p.display_name if hasattr(p, 'display_name') else p.name,
            family_name=p.family_name, given_name=p.given_name,
            form_of_address=p.form_of_address,
            gender=p.gender,
            body=f"{base}/oparl/v1/body/{body_id}",
            created=p.created, modified=p.modified,
        )
        for p in result["data"]
    ]
    return result


# ============================================================
# Meeting
# ============================================================
@router.get("/body/{body_id}/meeting")
def list_meetings(
    body_id: str, request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    meeting_state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    base = get_base_url(request)
    query = db.query(Meeting).filter(Meeting.body_id == body_id, Meeting.deleted == False)
    if meeting_state:
        query = query.filter(Meeting.meeting_state == meeting_state)
    query = query.order_by(Meeting.start.desc())
    
    result = paginate(query, page, page_size, base, f"/oparl/v1/body/{body_id}/meeting")
    result["data"] = [
        MeetingSchema(
            id=f"{base}/oparl/v1/meeting/{m.id}",
            name=m.name, meeting_state=m.meeting_state,
            cancelled=m.cancelled,
            start=m.start, end=m.end,
            organization=f"{base}/oparl/v1/organization/{m.organization_id}" if m.organization_id else None,
            created=m.created, modified=m.modified,
        )
        for m in result["data"]
    ]
    return result


@router.get("/meeting/{meeting_id}", response_model=MeetingSchema)
def get_meeting(meeting_id: str, request: Request, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(404, "Meeting not found")
    base = get_base_url(request)
    return MeetingSchema(
        id=f"{base}/oparl/v1/meeting/{m.id}",
        name=m.name, meeting_state=m.meeting_state,
        cancelled=m.cancelled, start=m.start, end=m.end,
        created=m.created, modified=m.modified,
    )


# ============================================================
# Paper
# ============================================================
@router.get("/body/{body_id}/paper")
def list_papers(
    body_id: str, request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    paper_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    base = get_base_url(request)
    query = db.query(Paper).filter(Paper.body_id == body_id, Paper.deleted == False)
    if paper_type:
        query = query.filter(Paper.paper_type == paper_type)
    query = query.order_by(Paper.date.desc())
    
    result = paginate(query, page, page_size, base, f"/oparl/v1/body/{body_id}/paper")
    result["data"] = [
        PaperSchema(
            id=f"{base}/oparl/v1/paper/{p.id}",
            name=p.name, reference=p.reference,
            date=p.date, paper_type=p.paper_type,
            body=f"{base}/oparl/v1/body/{body_id}",
            created=p.created, modified=p.modified,
        )
        for p in result["data"]
    ]
    return result


@router.get("/paper/{paper_id}", response_model=PaperSchema)
def get_paper(paper_id: str, request: Request, db: Session = Depends(get_db)):
    p = db.query(Paper).filter(Paper.id == paper_id).first()
    if not p:
        raise HTTPException(404, "Paper not found")
    base = get_base_url(request)
    return PaperSchema(
        id=f"{base}/oparl/v1/paper/{p.id}",
        name=p.name, reference=p.reference,
        date=p.date, paper_type=p.paper_type,
        body=f"{base}/oparl/v1/body/{p.body_id}",
        created=p.created, modified=p.modified,
    )


# ============================================================
# Search (non-OParl extension)
# ============================================================
@router.get("/search")
def search(
    request: Request,
    q: str = Query(..., min_length=2),
    body_id: Optional[str] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Full-text search across all OParl objects (aitema extension)."""
    base = get_base_url(request)
    results = []
    
    # Search Papers
    if not type or type == "paper":
        papers = db.query(Paper).filter(
            Paper.name.ilike(f"%{q}%"),
            Paper.deleted == False,
        )
        if body_id:
            papers = papers.filter(Paper.body_id == body_id)
        for p in papers.limit(20).all():
            results.append({
                "type": "paper",
                "id": f"{base}/oparl/v1/paper/{p.id}",
                "name": p.name,
                "reference": p.reference,
            })
    
    # Search Persons
    if not type or type == "person":
        persons = db.query(Person).filter(
            (Person.name.ilike(f"%{q}%") |
             Person.family_name.ilike(f"%{q}%") |
             Person.given_name.ilike(f"%{q}%")),
            Person.deleted == False,
        )
        if body_id:
            persons = persons.filter(Person.body_id == body_id)
        for p in persons.limit(20).all():
            results.append({
                "type": "person",
                "id": f"{base}/oparl/v1/person/{p.id}",
                "name": p.name or f"{p.given_name} {p.family_name}",
            })
    
    # Search Meetings
    if not type or type == "meeting":
        meetings = db.query(Meeting).filter(
            Meeting.name.ilike(f"%{q}%"),
            Meeting.deleted == False,
        )
        if body_id:
            meetings = meetings.filter(Meeting.body_id == body_id)
        for m in meetings.limit(20).all():
            results.append({
                "type": "meeting",
                "id": f"{base}/oparl/v1/meeting/{m.id}",
                "name": m.name,
                "start": m.start.isoformat() if m.start else None,
            })
    
    return {
        "query": q,
        "totalResults": len(results),
        "data": results,
    }
