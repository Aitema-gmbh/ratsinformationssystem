"""
Migration API Router

Provides endpoints for importing data from legacy RIS systems.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.migration import OParlMigrator, ALLRISMigrator

router = APIRouter(prefix="/api/admin/migration", tags=["Migration"])


@router.post("/oparl")
async def migrate_from_oparl(
    source_url: str,
    tenant_id: str = "default",
    db: Session = Depends(get_db),
):
    """Start migration from an OParl API source."""
    migrator = OParlMigrator(db, tenant_id, source_url)
    result = await migrator.migrate_all()
    return result.to_dict()


@router.post("/allris/csv")
async def migrate_from_allris_csv(
    tenant_id: str = "default",
    gremien: UploadFile = File(None),
    personen: UploadFile = File(None),
    vorlagen: UploadFile = File(None),
    sitzungen: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """Import ALLRIS data from CSV exports."""
    import csv
    import io
    
    csv_data = {}
    
    for name, file in [('gremien', gremien), ('personen', personen),
                       ('vorlagen', vorlagen), ('sitzungen', sitzungen)]:
        if file:
            content = await file.read()
            text = content.decode('utf-8-sig')  # Handle BOM
            reader = csv.DictReader(io.StringIO(text), delimiter=';')
            csv_data[name] = list(reader)
    
    if not csv_data:
        raise HTTPException(400, "Keine CSV-Dateien hochgeladen")
    
    migrator = ALLRISMigrator(db, tenant_id, "allris-csv")
    result = await migrator.migrate_from_csv(csv_data)
    return result.to_dict()


@router.get("/status")
async def migration_status():
    """Get current migration status."""
    return {
        "supported_sources": [
            {
                "type": "oparl",
                "name": "OParl API",
                "description": "Import von jedem OParl 1.0/1.1 kompatiblen System",
            },
            {
                "type": "allris_csv",
                "name": "ALLRIS CSV-Export",
                "description": "Import von ALLRIS CSV-Dateien (Gremien, Personen, Vorlagen, Sitzungen)",
            },
            {
                "type": "sessionnet",
                "name": "SessionNet",
                "description": "Import von Somacos SessionNet (geplant)",
                "status": "planned",
            },
        ]
    }
