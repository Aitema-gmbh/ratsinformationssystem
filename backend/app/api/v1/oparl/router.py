"""
aitema|RIS - OParl 1.1 REST API Endpoints
Provides OParl 1.1 compliant endpoints for all 12 object types.
https://dev.oparl.org/spezifikation/
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import Permission, get_current_user_optional, TokenPayload
from app.models.oparl import (
    AgendaItem,
    Body,
    Consultation,
    File,
    LegislativeTerm,
    Location,
    Meeting,
    Membership,
    Organization,
    Paper,
    Person,
    System,
)
from app.services.oparl_service import OParlService

router = APIRouter()


# ===================================================================
# Pagination helper
# ===================================================================

def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Items per page"),
):
    return {"page": page, "per_page": per_page}


def build_oparl_list_response(
    items: list[dict],
    total: int,
    page: int,
    per_page: int,
    base_url: str,
) -> dict:
    """Build an OParl-compliant paginated list response."""
    response = {
        "data": items,
        "pagination": {
            "totalElements": total,
            "elementsPerPage": per_page,
            "currentPage": page,
            "totalPages": (total + per_page - 1) // per_page,
        },
        "links": {
            "self": f"{base_url}?page={page}&per_page={per_page}",
        },
    }
    if page > 1:
        response["links"]["first"] = f"{base_url}?page=1&per_page={per_page}"
        response["links"]["prev"] = f"{base_url}?page={page-1}&per_page={per_page}"
    total_pages = (total + per_page - 1) // per_page
    if page < total_pages:
        response["links"]["next"] = f"{base_url}?page={page+1}&per_page={per_page}"
        response["links"]["last"] = f"{base_url}?page={total_pages}&per_page={per_page}"
    return response


# ===================================================================
# 1. System
# ===================================================================

@router.get("/system", summary="OParl System entry point")
async def get_system(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the OParl System object - the entry point for the OParl API.
    This is the starting point for any OParl client.
    """
    service = OParlService(db, str(request.base_url))
    system = await service.get_system()
    if not system:
        raise HTTPException(status_code=404, detail="System not configured")
    return system


# ===================================================================
# 2. Body (Koerperschaft)
# ===================================================================

@router.get("/body", summary="List all bodies")
async def list_bodies(
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all governmental bodies (Koerperschaften) in this system."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(Body, **pagination)
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body"
    )


@router.get("/body/{body_id}", summary="Get a single body")
async def get_body(
    body_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get a single governmental body by its ID."""
    service = OParlService(db, str(request.base_url))
    body = await service.get_object(Body, body_id)
    if not body:
        raise HTTPException(status_code=404, detail="Body not found")
    return body


# ===================================================================
# 3. LegislativeTerm (Wahlperiode)
# ===================================================================

@router.get("/body/{body_id}/legislative-term", summary="List legislative terms")
async def list_legislative_terms(
    body_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all legislative terms (Wahlperioden) of a body."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(
        LegislativeTerm, body_id=body_id, **pagination
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body/{body_id}/legislative-term"
    )


@router.get("/legislative-term/{term_id}", summary="Get a legislative term")
async def get_legislative_term(
    term_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    term = await service.get_object(LegislativeTerm, term_id)
    if not term:
        raise HTTPException(status_code=404, detail="LegislativeTerm not found")
    return term


# ===================================================================
# 4. Organization (Gremium/Fraktion)
# ===================================================================

@router.get("/body/{body_id}/organization", summary="List organizations")
async def list_organizations(
    body_id: UUID,
    request: Request,
    organization_type: Optional[str] = Query(None, description="Filter by type"),
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all organizations (Gremien, Fraktionen) of a body."""
    service = OParlService(db, str(request.base_url))
    filters = {}
    if organization_type:
        filters["organization_type"] = organization_type
    items, total = await service.list_objects(
        Organization, body_id=body_id, **pagination, **filters
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body/{body_id}/organization"
    )


@router.get("/organization/{org_id}", summary="Get an organization")
async def get_organization(
    org_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    org = await service.get_object(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


# ===================================================================
# 5. Person
# ===================================================================

@router.get("/body/{body_id}/person", summary="List persons")
async def list_persons(
    body_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all persons associated with a body."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(Person, body_id=body_id, **pagination)
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body/{body_id}/person"
    )


@router.get("/person/{person_id}", summary="Get a person")
async def get_person(
    person_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    person = await service.get_object(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


# ===================================================================
# 6. Membership (Mitgliedschaft)
# ===================================================================

@router.get("/organization/{org_id}/membership", summary="List memberships of an org")
async def list_memberships_by_org(
    org_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all memberships of an organization."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(
        Membership, organization_id=org_id, **pagination
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/organization/{org_id}/membership"
    )


@router.get("/person/{person_id}/membership", summary="List memberships of a person")
async def list_memberships_by_person(
    person_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all memberships of a person."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(
        Membership, person_id=person_id, **pagination
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/person/{person_id}/membership"
    )


@router.get("/membership/{membership_id}", summary="Get a membership")
async def get_membership(
    membership_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    membership = await service.get_object(Membership, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


# ===================================================================
# 7. Meeting (Sitzung)
# ===================================================================

@router.get("/body/{body_id}/meeting", summary="List meetings")
async def list_meetings(
    body_id: UUID,
    request: Request,
    meeting_state: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="Filter: start >= date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter: start <= date (ISO)"),
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all meetings (Sitzungen) of a body with optional filters."""
    service = OParlService(db, str(request.base_url))
    filters = {}
    if meeting_state:
        filters["meeting_state"] = meeting_state
    items, total = await service.list_objects(
        Meeting, body_id=body_id, **pagination, **filters
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body/{body_id}/meeting"
    )


@router.get("/meeting/{meeting_id}", summary="Get a meeting")
async def get_meeting(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    meeting = await service.get_object(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


# ===================================================================
# 8. AgendaItem (Tagesordnungspunkt)
# ===================================================================

@router.get("/meeting/{meeting_id}/agenda-item", summary="List agenda items")
async def list_agenda_items(
    meeting_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all agenda items of a meeting."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(
        AgendaItem, meeting_id=meeting_id, **pagination
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/meeting/{meeting_id}/agenda-item"
    )


@router.get("/agenda-item/{item_id}", summary="Get an agenda item")
async def get_agenda_item(
    item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    item = await service.get_object(AgendaItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="AgendaItem not found")
    return item


# ===================================================================
# 9. Paper (Vorlage/Drucksache)
# ===================================================================

@router.get("/body/{body_id}/paper", summary="List papers")
async def list_papers(
    body_id: UUID,
    request: Request,
    paper_type: Optional[str] = Query(None),
    reference: Optional[str] = Query(None),
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all papers (Vorlagen/Drucksachen) of a body."""
    service = OParlService(db, str(request.base_url))
    filters = {}
    if paper_type:
        filters["paper_type"] = paper_type
    if reference:
        filters["reference"] = reference
    items, total = await service.list_objects(
        Paper, body_id=body_id, **pagination, **filters
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/body/{body_id}/paper"
    )


@router.get("/paper/{paper_id}", summary="Get a paper")
async def get_paper(
    paper_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    paper = await service.get_object(Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


# ===================================================================
# 10. Consultation (Beratung)
# ===================================================================

@router.get("/paper/{paper_id}/consultation", summary="List consultations of a paper")
async def list_consultations(
    paper_id: UUID,
    request: Request,
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List all consultations (Beratungen) for a paper."""
    service = OParlService(db, str(request.base_url))
    items, total = await service.list_objects(
        Consultation, paper_id=paper_id, **pagination
    )
    return build_oparl_list_response(
        items, total, pagination["page"], pagination["per_page"],
        f"{request.base_url}api/v1/oparl/paper/{paper_id}/consultation"
    )


@router.get("/consultation/{consultation_id}", summary="Get a consultation")
async def get_consultation(
    consultation_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    consultation = await service.get_object(Consultation, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultation


# ===================================================================
# 11. File (Datei)
# ===================================================================

@router.get("/file/{file_id}", summary="Get a file metadata")
async def get_file(
    file_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get file metadata. Use accessUrl/downloadUrl for actual file content."""
    service = OParlService(db, str(request.base_url))
    file = await service.get_object(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


# ===================================================================
# 12. Location (Ort)
# ===================================================================

@router.get("/location/{location_id}", summary="Get a location")
async def get_location(
    location_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = OParlService(db, str(request.base_url))
    location = await service.get_object(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


# ===================================================================
# Search (OParl-Extension)
# ===================================================================

@router.get("/search", summary="Full-text search across all OParl objects")
async def search_oparl(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    object_type: Optional[str] = Query(None, description="Filter by OParl type"),
    body_id: Optional[UUID] = Query(None, description="Filter by body"),
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """
    Full-text search across all OParl objects.
    Uses Elasticsearch for fast, relevance-ranked results.
    """
    from app.services.search_service import SearchService
    search = SearchService()
    results = await search.search(
        query=q,
        object_type=object_type,
        body_id=str(body_id) if body_id else None,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )
    return results
