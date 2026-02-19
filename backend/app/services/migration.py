"""
ALLRIS / SessionNet Migration Service

Migrates data from legacy RIS systems:
- ALLRIS (CC e-gov / Sternberg) 
- SessionNet (Somacos)

Both systems typically expose data via OPARL or proprietary APIs/database exports.
"""
import json
import uuid
from datetime import datetime, date
from typing import Optional, List
from dataclasses import dataclass
import httpx
from sqlalchemy.orm import Session

from app.models.oparl import (
    Body, Organization, Person, Membership, Meeting,
    AgendaItem, Paper, Consultation, File, Location,
    LegislativeTerm,
)


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    source: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    bodies: int = 0
    organizations: int = 0
    persons: int = 0
    memberships: int = 0
    meetings: int = 0
    agenda_items: int = 0
    papers: int = 0
    consultations: int = 0
    files: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @property
    def total(self):
        return (self.bodies + self.organizations + self.persons +
                self.memberships + self.meetings + self.agenda_items +
                self.papers + self.consultations + self.files)

    def to_dict(self):
        return {
            'source': self.source,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_migrated': self.total,
            'bodies': self.bodies,
            'organizations': self.organizations,
            'persons': self.persons,
            'memberships': self.memberships,
            'meetings': self.meetings,
            'agenda_items': self.agenda_items,
            'papers': self.papers,
            'consultations': self.consultations,
            'files': self.files,
            'errors': self.errors[:50],  # Limit error list
            'error_count': len(self.errors),
        }


class OParlMigrator:
    """
    Generic OParl-based migrator.
    
    Works with any OParl 1.0/1.1 API including:
    - ALLRIS (if OParl module enabled)
    - SessionNet (if OParl module enabled)
    - Any other OParl-compliant system
    """

    def __init__(self, session: Session, tenant_id: str, source_url: str):
        self.session = session
        self.tenant_id = tenant_id
        self.source_url = source_url.rstrip('/')
        self.id_map = {}  # source_id -> new_id mapping
        self.result = MigrationResult(source=source_url, started_at=datetime.utcnow())

    async def migrate_all(self) -> MigrationResult:
        """Run full migration from OParl source."""
        try:
            # 1. Get system info
            system = await self._fetch(self.source_url)
            
            # 2. Get bodies
            body_list_url = system.get('body', f"{self.source_url}/body")
            await self._migrate_bodies(body_list_url)
            
            self.result.completed_at = datetime.utcnow()
        except Exception as e:
            self.result.errors.append(f"Migration failed: {str(e)}")
        
        return self.result

    async def _fetch(self, url: str) -> dict:
        """Fetch OParl data from source."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def _fetch_paginated(self, url: str) -> List[dict]:
        """Fetch all pages of an OParl list."""
        all_items = []
        current_url = url
        
        while current_url:
            data = await self._fetch(current_url)
            items = data.get('data', [])
            all_items.extend(items)
            
            # OParl pagination
            links = data.get('links', {})
            current_url = links.get('next')
        
        return all_items

    async def _migrate_bodies(self, url: str):
        """Migrate Body objects."""
        bodies = await self._fetch_paginated(url)
        
        for src in bodies:
            try:
                body = Body(
                    tenant_id=self.tenant_id,
                    oparl_id=src.get('id'),
                    name=src.get('name', 'Unbekannt'),
                    short_name=src.get('shortName'),
                    body_type=src.get('bodyType'),
                    classification=src.get('classification'),
                    ags=src.get('ags'),
                    rgs=src.get('rgs'),
                    contact_email=src.get('contactEmail'),
                    web=src.get('web'),
                )
                self.session.add(body)
                self.session.flush()
                self.id_map[src.get('id')] = body.id
                self.result.bodies += 1
                
                # Migrate sub-objects
                if src.get('organization'):
                    await self._migrate_organizations(src['organization'], body.id)
                if src.get('person'):
                    await self._migrate_persons(src['person'], body.id)
                if src.get('meeting'):
                    await self._migrate_meetings(src['meeting'], body.id)
                if src.get('paper'):
                    await self._migrate_papers(src['paper'], body.id)
                    
            except Exception as e:
                self.result.errors.append(f"Body {src.get('name')}: {str(e)}")

        self.session.commit()

    async def _migrate_organizations(self, url: str, body_id: str):
        """Migrate Organization objects."""
        orgs = await self._fetch_paginated(url)
        
        for src in orgs:
            try:
                org = Organization(
                    tenant_id=self.tenant_id,
                    body_id=body_id,
                    oparl_id=src.get('id'),
                    name=src.get('name', 'Unbekannt'),
                    short_name=src.get('shortName'),
                    organization_type=src.get('organizationType'),
                    classification=src.get('classification'),
                    start_date=self._parse_date(src.get('startDate')),
                    end_date=self._parse_date(src.get('endDate')),
                )
                self.session.add(org)
                self.session.flush()
                self.id_map[src.get('id')] = org.id
                self.result.organizations += 1
            except Exception as e:
                self.result.errors.append(f"Org {src.get('name')}: {str(e)}")

    async def _migrate_persons(self, url: str, body_id: str):
        """Migrate Person objects."""
        persons = await self._fetch_paginated(url)
        
        for src in persons:
            try:
                person = Person(
                    tenant_id=self.tenant_id,
                    body_id=body_id,
                    oparl_id=src.get('id'),
                    name=src.get('name'),
                    family_name=src.get('familyName'),
                    given_name=src.get('givenName'),
                    form_of_address=src.get('formOfAddress'),
                    gender=src.get('gender'),
                    email=src.get('email', []),
                    phone=src.get('phone', []),
                    status=src.get('status', []),
                )
                self.session.add(person)
                self.session.flush()
                self.id_map[src.get('id')] = person.id
                self.result.persons += 1
            except Exception as e:
                self.result.errors.append(f"Person {src.get('name')}: {str(e)}")

    async def _migrate_meetings(self, url: str, body_id: str):
        """Migrate Meeting objects."""
        meetings = await self._fetch_paginated(url)
        
        for src in meetings:
            try:
                meeting = Meeting(
                    tenant_id=self.tenant_id,
                    body_id=body_id,
                    oparl_id=src.get('id'),
                    name=src.get('name', 'Unbekannte Sitzung'),
                    meeting_state=src.get('meetingState', 'completed'),
                    cancelled=src.get('cancelled', False),
                    start=self._parse_datetime(src.get('start')),
                    end=self._parse_datetime(src.get('end')),
                    organization_id=self.id_map.get(src.get('organization')),
                )
                self.session.add(meeting)
                self.session.flush()
                self.id_map[src.get('id')] = meeting.id
                self.result.meetings += 1
                
                # Migrate agenda items
                for ai_data in src.get('agendaItem', []):
                    if isinstance(ai_data, str):
                        # URL reference - fetch individually
                        ai_data = await self._fetch(ai_data)
                    self._migrate_agenda_item(ai_data, meeting.id)
                    
            except Exception as e:
                self.result.errors.append(f"Meeting {src.get('name')}: {str(e)}")

    def _migrate_agenda_item(self, src: dict, meeting_id: str):
        """Migrate a single agenda item."""
        try:
            item = AgendaItem(
                tenant_id=self.tenant_id,
                meeting_id=meeting_id,
                oparl_id=src.get('id'),
                name=src.get('name', ''),
                number=src.get('number'),
                order=src.get('order', 0),
                public=src.get('public', True),
                result=src.get('result'),
                resolution_text=src.get('resolutionText'),
            )
            self.session.add(item)
            self.session.flush()
            self.id_map[src.get('id')] = item.id
            self.result.agenda_items += 1
        except Exception as e:
            self.result.errors.append(f"AgendaItem: {str(e)}")

    async def _migrate_papers(self, url: str, body_id: str):
        """Migrate Paper objects."""
        papers = await self._fetch_paginated(url)
        
        for src in papers:
            try:
                paper = Paper(
                    tenant_id=self.tenant_id,
                    body_id=body_id,
                    oparl_id=src.get('id'),
                    name=src.get('name', 'Unbekannte Drucksache'),
                    reference=src.get('reference'),
                    date=self._parse_date(src.get('date')),
                    paper_type=src.get('paperType'),
                )
                self.session.add(paper)
                self.session.flush()
                self.id_map[src.get('id')] = paper.id
                self.result.papers += 1
            except Exception as e:
                self.result.errors.append(f"Paper {src.get('name')}: {str(e)}")

    @staticmethod
    def _parse_date(value) -> Optional[date]:
        if not value:
            return None
        try:
            return date.fromisoformat(value[:10])
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None


class ALLRISMigrator(OParlMigrator):
    """
    ALLRIS-specific migrator.
    
    ALLRIS by CC e-gov (now Sternberg) stores data in a SQL Server database.
    This migrator supports:
    - Direct database access (ODBC)
    - ALLRIS OParl API
    - CSV/XML export files
    """

    async def migrate_from_csv(self, csv_data: dict) -> MigrationResult:
        """
        Migrate from ALLRIS CSV exports.
        
        Expected files:
        - gremien.csv -> Organizations
        - personen.csv -> Persons  
        - sitzungen.csv -> Meetings
        - vorlagen.csv -> Papers
        - tops.csv -> AgendaItems
        """
        self.result = MigrationResult(source='ALLRIS CSV', started_at=datetime.utcnow())
        
        if 'gremien' in csv_data:
            self._import_gremien_csv(csv_data['gremien'])
        if 'personen' in csv_data:
            self._import_personen_csv(csv_data['personen'])
        if 'vorlagen' in csv_data:
            self._import_vorlagen_csv(csv_data['vorlagen'])
        if 'sitzungen' in csv_data:
            self._import_sitzungen_csv(csv_data['sitzungen'])
        
        self.session.commit()
        self.result.completed_at = datetime.utcnow()
        return self.result

    def _import_gremien_csv(self, rows: list):
        """Import ALLRIS Gremien (committees) from CSV."""
        for row in rows:
            try:
                org = Organization(
                    tenant_id=self.tenant_id,
                    body_id=self.id_map.get('body', ''),
                    name=row.get('GRNAME', ''),
                    short_name=row.get('GRKURZ', ''),
                    organization_type=self._map_allris_gremium_type(row.get('GRTYP', '')),
                )
                self.session.add(org)
                self.session.flush()
                allris_id = row.get('GRNR', '')
                if allris_id:
                    self.id_map[f"gremium_{allris_id}"] = org.id
                self.result.organizations += 1
            except Exception as e:
                self.result.errors.append(f"Gremium CSV: {str(e)}")

    def _import_personen_csv(self, rows: list):
        for row in rows:
            try:
                person = Person(
                    tenant_id=self.tenant_id,
                    body_id=self.id_map.get('body', ''),
                    family_name=row.get('PENAME', ''),
                    given_name=row.get('PVORNAME', ''),
                    form_of_address=row.get('PANREDE', ''),
                    name=f"{row.get('PVORNAME', '')} {row.get('PENAME', '')}".strip(),
                )
                self.session.add(person)
                self.session.flush()
                allris_id = row.get('PENR', '')
                if allris_id:
                    self.id_map[f"person_{allris_id}"] = person.id
                self.result.persons += 1
            except Exception as e:
                self.result.errors.append(f"Person CSV: {str(e)}")

    def _import_vorlagen_csv(self, rows: list):
        for row in rows:
            try:
                paper = Paper(
                    tenant_id=self.tenant_id,
                    body_id=self.id_map.get('body', ''),
                    name=row.get('VOBETREFF', ''),
                    reference=row.get('VONR', ''),
                    paper_type=row.get('VOTYP', 'Vorlage'),
                    date=self._parse_date(row.get('VODATUM')),
                )
                self.session.add(paper)
                self.session.flush()
                self.result.papers += 1
            except Exception as e:
                self.result.errors.append(f"Vorlage CSV: {str(e)}")

    def _import_sitzungen_csv(self, rows: list):
        for row in rows:
            try:
                org_id = self.id_map.get(f"gremium_{row.get('SIGRNR', '')}")
                meeting = Meeting(
                    tenant_id=self.tenant_id,
                    body_id=self.id_map.get('body', ''),
                    name=row.get('SIBETREFF', f"Sitzung {row.get('SIGRNR', '')}"),
                    meeting_state='completed',
                    start=self._parse_datetime(row.get('SIDATUM')),
                    organization_id=org_id,
                )
                self.session.add(meeting)
                self.session.flush()
                self.result.meetings += 1
            except Exception as e:
                self.result.errors.append(f"Sitzung CSV: {str(e)}")

    @staticmethod
    def _map_allris_gremium_type(allris_type: str) -> str:
        mapping = {
            'A': 'ausschuss',
            'F': 'fraktion',
            'R': 'ausschuss',  # Rat = Hauptausschuss
            'B': 'sonstiges',  # Beirat
            'V': 'verwaltung',
        }
        return mapping.get(allris_type, 'sonstiges')
