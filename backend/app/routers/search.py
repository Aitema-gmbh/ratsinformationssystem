"""
aitema|RIS - Search Router

FastAPI Router fuer Volltextsuche:
- GET  /api/v1/search                 - Volltextsuche mit Filtern
- GET  /api/v1/search/autocomplete    - Typeahead-Vorschlaege
- GET  /api/v1/search/facets          - Suche mit aggregierten Facetten
- POST /api/v1/admin/search/reindex   - Vollstaendiger Reindex
"""
from __future__ import annotations

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.oparl import Paper, Meeting, Person, Organization
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/v1", tags=["Suche"])

# ============================================================
# Pydantic Schemas
# ============================================================

class SearchResponse(BaseModel):
    data: list[dict]
    total: int
    page: int
    per_page: int
    total_pages: int
    facets: dict
    query: str

class AutocompleteItem(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    reference: Optional[str] = None
    paper_type: Optional[str] = None
    meeting_state: Optional[str] = None
    score: float = 0.0

class AutocompleteResponse(BaseModel):
    suggestions: list[AutocompleteItem]
    query: str

class ReindexResponse(BaseModel):
    status: str
    indexed: int
    duration_ms: int
    breakdown: dict

# ============================================================
# GET /api/v1/search
# ============================================================

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(default="", description="Suchbegriff"),
    type: Optional[str] = Query(default=None, description="Typ: paper, meeting, person"),
    gremium: Optional[str] = Query(default=None, description="Gremiumsname-Filter"),
    year: Optional[int] = Query(default=None, description="Jahres-Filter"),
    status: Optional[str] = Query(default=None, description="Status-Filter"),
    body_id: Optional[str] = Query(default=None, description="Koerperschaft-ID"),
    tenant_id: Optional[str] = Query(default=None, description="Tenant-ID"),
    page: int = Query(default=1, ge=1, description="Seite"),
    size: int = Query(default=20, ge=1, le=100, description="Ergebnisse pro Seite"),
):
    """
    Volltextsuche ueber Papers, Meetings und Personen.

    Unterstuetzt:
    - Fuzzy-Matching und Stemming (Deutsch)
    - Highlighting mit &lt;mark&gt; Tags
    - Filter: Typ, Gremium, Jahr, Status
    - Pagination
    - Facetten (Aggregationen)
    """
    if not q or len(q.strip()) < 2:
        return SearchResponse(
            data=[],
            total=0,
            page=page,
            per_page=size,
            total_pages=0,
            facets={},
            query=q,
        )

    types = [type] if type else None
    svc = SearchService()
    try:
        result = await svc.search(
            query=q.strip(),
            types=types,
            tenant_id=tenant_id,
            body_id=body_id,
            gremium=gremium,
            year=year,
            status=status,
            page=page,
            size=size,
        )
    finally:
        await svc.close()

    return SearchResponse(
        data=result.data,
        total=result.total,
        page=result.page,
        per_page=result.per_page,
        total_pages=result.total_pages,
        facets=result.facets,
        query=q,
    )

# ============================================================
# GET /api/v1/search/autocomplete
# ============================================================

@router.get("/search/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(default="", description="Suchpraefix (mind. 3 Zeichen)"),
    type: Optional[str] = Query(default=None, description="Typ: paper, meeting, person"),
    tenant_id: Optional[str] = Query(default=None),
    limit: int = Query(default=8, ge=1, le=20),
):
    """
    Typeahead-Autocomplete-Vorschlaege.

    Nutzt Edge-NGram Analyse (min 3 / max 15 Gramm).
    Gibt max. 8 Vorschlaege zurueck.
    """
    if len(q.strip()) < 3:
        return AutocompleteResponse(suggestions=[], query=q)

    svc = SearchService()
    try:
        suggestions = await svc.autocomplete(
            prefix=q.strip(),
            type=type,
            limit=limit,
            tenant_id=tenant_id,
        )
    finally:
        await svc.close()

    return AutocompleteResponse(
        suggestions=[AutocompleteItem(**s) for s in suggestions],
        query=q,
    )

# ============================================================
# GET /api/v1/search/facets
# ============================================================

@router.get("/search/facets")
async def search_facets(
    q: str = Query(default="", description="Suchbegriff"),
    tenant_id: Optional[str] = Query(default=None),
    body_id: Optional[str] = Query(default=None),
):
    """
    Volltext-Suche mit aggregierten Facetten.

    Gibt Ergebnisse + Facetten (by_type, by_paper_type, by_organization, by_year).
    """
    if not q or len(q.strip()) < 2:
        return {"results": {"data": [], "total": 0}, "facets": {}, "query": q}

    svc = SearchService()
    try:
        result = await svc.search_with_facets(
            query=q.strip(),
            tenant_id=tenant_id,
            body_id=body_id,
        )
    finally:
        await svc.close()

    return {**result, "query": q}

# ============================================================
# POST /api/v1/admin/search/reindex
# ============================================================

@router.post("/admin/search/reindex", response_model=ReindexResponse)
async def reindex(db: Session = Depends(get_db)):
    """
    Vollstaendiger Elasticsearch-Reindex aller OParl-Objekte.

    Indexiert Papers, Meetings und Persons separat in drei Indizes:
    - {prefix}_ris_papers
    - {prefix}_ris_meetings
    - {prefix}_ris_persons
    """
    start = datetime.utcnow()
    svc = SearchService()

    try:
        # Papers aufsammeln
        papers_data = []
        papers = db.query(Paper).filter(Paper.deleted == False).all()
        for p in papers:
            papers_data.append({
                "oparl_id": p.id,
                "oparl_type": "paper",
                "body_id": p.body_id,
                "tenant_id": getattr(p, "tenant_id", "public"),
                "name": p.name,
                "reference": p.reference,
                "paper_type": p.paper_type,
                "date": p.date.isoformat() if p.date else None,
                "created": p.created.isoformat() if p.created else None,
                "modified": p.modified.isoformat() if p.modified else None,
            })

        # Meetings aufsammeln
        meetings_data = []
        meetings = db.query(Meeting).filter(Meeting.deleted == False).all()
        for m in meetings:
            # Organisations-Namen ermitteln
            org_names = []
            for ai in m.agenda_items:
                if hasattr(ai, "organizations"):
                    for o in ai.organizations:
                        if o.name and o.name not in org_names:
                            org_names.append(o.name)

            meetings_data.append({
                "oparl_id": m.id,
                "oparl_type": "meeting",
                "body_id": m.body_id,
                "tenant_id": getattr(m, "tenant_id", "public"),
                "name": m.name,
                "meeting_state": m.meeting_state,
                "start": m.start.isoformat() if m.start else None,
                "end": m.end.isoformat() if m.end else None,
                "organization_name": org_names[0] if org_names else None,
                "created": m.created.isoformat() if m.created else None,
                "modified": m.modified.isoformat() if m.modified else None,
            })

        # Persons aufsammeln
        persons_data = []
        persons = db.query(Person).filter(Person.deleted == False).all()
        for p in persons:
            full_name = " ".join(filter(None, [p.given_name, p.family_name]))
            persons_data.append({
                "oparl_id": p.id,
                "oparl_type": "person",
                "body_id": p.body_id,
                "tenant_id": getattr(p, "tenant_id", "public"),
                "name": full_name or p.name,
                "family_name": p.family_name,
                "given_name": p.given_name,
                "created": p.created.isoformat() if p.created else None,
                "modified": p.modified.isoformat() if p.modified else None,
            })

        # Indexieren
        indexed_papers = await svc.index_all_papers(papers_data)
        indexed_meetings = await svc.index_all_meetings(meetings_data)
        indexed_persons = await svc.index_all_persons(persons_data)

        total = indexed_papers + indexed_meetings + indexed_persons
        duration = int((datetime.utcnow() - start).total_seconds() * 1000)

        return ReindexResponse(
            status="completed",
            indexed=total,
            duration_ms=duration,
            breakdown={
                "papers": indexed_papers,
                "meetings": indexed_meetings,
                "persons": indexed_persons,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex fehlgeschlagen: {str(e)}")
    finally:
        await svc.close()
