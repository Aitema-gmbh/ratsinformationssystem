"""
aitema|RIS - Admin-API

Verwaltungs-Endpunkte:
- POST /admin/reindex - Elasticsearch Reindex triggern
- GET  /admin/stats   - System-Statistiken
- POST /admin/tenant  - Neuen Tenant anlegen
- PUT  /admin/tenant/{id} - Tenant bearbeiten
- GET  /admin/health  - Detaillierter Health-Check (DB, Redis, Elasticsearch)
- POST /admin/seed    - Demo-Daten generieren
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, create_tenant_schema
from app.models.oparl import (
    OParlSystem, Body, Organization, Person, Membership,
    Meeting, AgendaItem, Paper, Consultation, File,
)
from app.services.search_service import SearchService
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["Admin"])

# ============================================================
# Schemas
# ============================================================

class TenantCreate(BaseModel):
    name: str
    slug: str
    contact_email: Optional[str] = None
    website: Optional[str] = None

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    active: Optional[bool] = None

class ReindexResponse(BaseModel):
    status: str
    indexed: int
    duration_ms: int

class StatsResponse(BaseModel):
    bodies: int
    organizations: int
    persons: int
    meetings: int
    papers: int
    agenda_items: int
    files: int
    consultations: int

class HealthResponse(BaseModel):
    status: str
    database: dict
    redis: dict
    elasticsearch: dict
    timestamp: str


# ============================================================
# Reindex
# ============================================================

@router.post("/reindex", response_model=ReindexResponse)
async def trigger_reindex(db: Session = Depends(get_db)):
    """
    Elasticsearch Reindex aller OParl-Objekte triggern.
    Sammelt alle Papers, Meetings und Persons und indexiert sie.
    """
    start = datetime.utcnow()
    search = SearchService()

    try:
        objects = []

        # Papers indexieren
        papers = db.query(Paper).filter(Paper.deleted == False).all()
        for p in papers:
            objects.append({
                "oparl_id": p.id,
                "oparl_type": "paper",
                "body_id": p.body_id,
                "tenant": p.tenant_id,
                "name": p.name,
                "reference": p.reference,
                "paper_type": p.paper_type,
                "date": p.date.isoformat() if p.date else None,
                "created": p.created.isoformat() if p.created else None,
                "modified": p.modified.isoformat() if p.modified else None,
            })

        # Meetings indexieren
        meetings = db.query(Meeting).filter(Meeting.deleted == False).all()
        for m in meetings:
            objects.append({
                "oparl_id": m.id,
                "oparl_type": "meeting",
                "body_id": m.body_id,
                "tenant": m.tenant_id,
                "name": m.name,
                "meeting_state": m.meeting_state,
                "start": m.start.isoformat() if m.start else None,
                "end": m.end.isoformat() if m.end else None,
                "created": m.created.isoformat() if m.created else None,
                "modified": m.modified.isoformat() if m.modified else None,
            })

        # Persons indexieren
        persons = db.query(Person).filter(Person.deleted == False).all()
        for p in persons:
            display_name = p.name or f"{p.given_name} {p.family_name}"
            objects.append({
                "oparl_id": p.id,
                "oparl_type": "person",
                "body_id": p.body_id,
                "tenant": p.tenant_id,
                "name": display_name,
                "created": p.created.isoformat() if p.created else None,
                "modified": p.modified.isoformat() if p.modified else None,
            })

        # Organizations indexieren
        orgs = db.query(Organization).filter(Organization.deleted == False).all()
        for o in orgs:
            objects.append({
                "oparl_id": o.id,
                "oparl_type": "organization",
                "body_id": o.body_id,
                "tenant": o.tenant_id,
                "name": o.name,
                "organization_type": o.organization_type,
                "created": o.created.isoformat() if o.created else None,
                "modified": o.modified.isoformat() if o.modified else None,
            })

        indexed = await search.reindex_all(objects)

        duration = int((datetime.utcnow() - start).total_seconds() * 1000)
        return ReindexResponse(
            status="completed",
            indexed=indexed,
            duration_ms=duration,
        )
    finally:
        await search.close()


# ============================================================
# Statistiken
# ============================================================

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """System-Statistiken: Anzahl aller OParl-Objekte."""
    return StatsResponse(
        bodies=db.query(Body).filter(Body.deleted == False).count(),
        organizations=db.query(Organization).filter(Organization.deleted == False).count(),
        persons=db.query(Person).filter(Person.deleted == False).count(),
        meetings=db.query(Meeting).filter(Meeting.deleted == False).count(),
        papers=db.query(Paper).filter(Paper.deleted == False).count(),
        agenda_items=db.query(AgendaItem).count(),
        files=db.query(File).count(),
        consultations=db.query(Consultation).count(),
    )


# ============================================================
# Tenant-Verwaltung
# ============================================================

@router.post("/tenant")
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    """Neuen Tenant (Mandant / Kommune) anlegen."""
    # System-Eintrag pruefen/erstellen
    system = db.query(OParlSystem).first()
    if not system:
        system = OParlSystem(
            name="aitema|Rats",
            oparl_version="https://schema.oparl.org/1.1/",
            vendor="https://aitema.de",
            product="https://aitema.de/rats",
        )
        db.add(system)
        db.flush()

    # Body als Koerperschaft anlegen
    body = Body(
        name=data.name,
        short_name=data.slug,
        tenant_id=data.slug,
        contact_email=data.contact_email,
        web=data.website,
    )
    db.add(body)
    db.commit()

    # Tenant-Schema erstellen (optional, fuer Schema-Isolation)
    try:
        create_tenant_schema(data.slug)
    except Exception as e:
        # Schema-Erstellung ist optional
        pass

    return {
        "status": "created",
        "tenant": {
            "id": body.id,
            "name": data.name,
            "slug": data.slug,
        },
    }


@router.put("/tenant/{tenant_id}")
def update_tenant(
    tenant_id: str,
    data: TenantUpdate,
    db: Session = Depends(get_db),
):
    """Tenant (Koerperschaft) bearbeiten."""
    body = db.query(Body).filter(
        (Body.id == tenant_id) | (Body.short_name == tenant_id)
    ).first()

    if not body:
        raise HTTPException(404, "Tenant nicht gefunden")

    if data.name is not None:
        body.name = data.name
    if data.contact_email is not None:
        body.contact_email = data.contact_email
    if data.website is not None:
        body.web = data.website
    if data.active is not None:
        body.deleted = not data.active

    body.modified = datetime.utcnow()
    db.commit()

    return {
        "status": "updated",
        "tenant": {
            "id": body.id,
            "name": body.name,
            "active": not body.deleted,
        },
    }


# ============================================================
# Health-Check
# ============================================================

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Detaillierter Health-Check fuer DB, Redis und Elasticsearch.
    """
    result = {
        "status": "healthy",
        "database": {"status": "unknown"},
        "redis": {"status": "unknown"},
        "elasticsearch": {"status": "unknown"},
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Database
    try:
        db.execute(text("SELECT 1"))
        tables = db.execute(text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = public"
        )).scalar()
        result["database"] = {
            "status": "healthy",
            "tables": tables,
        }
    except Exception as e:
        result["database"] = {"status": "unhealthy", "error": str(e)}
        result["status"] = "degraded"

    # Redis
    try:
        from redis import Redis as SyncRedis
        r = SyncRedis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        info = r.info("memory")
        result["redis"] = {
            "status": "healthy",
            "used_memory_human": info.get("used_memory_human", "unknown"),
        }
        r.close()
    except Exception as e:
        result["redis"] = {"status": "unhealthy", "error": str(e)}
        result["status"] = "degraded"

    # Elasticsearch
    try:
        search = SearchService()
        es_info = await search.client.info()
        result["elasticsearch"] = {
            "status": "healthy",
            "cluster": es_info.get("cluster_name", "unknown"),
            "version": es_info.get("version", {}).get("number", "unknown"),
        }
        await search.close()
    except Exception as e:
        result["elasticsearch"] = {"status": "unhealthy", "error": str(e)}
        result["status"] = "degraded"

    return result


# ============================================================
# Demo-Daten
# ============================================================

@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """Demo-Daten fuer eine Musterkommune generieren."""
    from app.seeds.demo_data import seed_musterstadt

    try:
        result = seed_musterstadt(db)
        return {
            "status": "success",
            "message": "Demo-Daten erfolgreich erstellt",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(500, f"Seed fehlgeschlagen: {str(e)}")
