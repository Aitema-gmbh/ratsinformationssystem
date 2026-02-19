"""
aitema|RIS - OParl Business Logic Service
Handles OParl-compliant serialization and business rules.
"""
from __future__ import annotations

from typing import Any, Optional, Type
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
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

settings = get_settings()

# OParl type URIs
OPARL_TYPE_MAP = {
    System: "https://schema.oparl.org/1.1/System",
    Body: "https://schema.oparl.org/1.1/Body",
    LegislativeTerm: "https://schema.oparl.org/1.1/LegislativeTerm",
    Organization: "https://schema.oparl.org/1.1/Organization",
    Person: "https://schema.oparl.org/1.1/Person",
    Membership: "https://schema.oparl.org/1.1/Membership",
    Meeting: "https://schema.oparl.org/1.1/Meeting",
    AgendaItem: "https://schema.oparl.org/1.1/AgendaItem",
    Paper: "https://schema.oparl.org/1.1/Paper",
    Consultation: "https://schema.oparl.org/1.1/Consultation",
    File: "https://schema.oparl.org/1.1/File",
    Location: "https://schema.oparl.org/1.1/Location",
}

# URL path segments for each type
OPARL_URL_SEGMENT = {
    System: "system",
    Body: "body",
    LegislativeTerm: "legislative-term",
    Organization: "organization",
    Person: "person",
    Membership: "membership",
    Meeting: "meeting",
    AgendaItem: "agenda-item",
    Paper: "paper",
    Consultation: "consultation",
    File: "file",
    Location: "location",
}


class OParlService:
    """
    Service for OParl-compliant data access and serialization.
    All responses conform to the OParl 1.1 specification.
    """

    def __init__(self, db: AsyncSession, base_url: str) -> None:
        self.db = db
        self.base_url = base_url.rstrip("/")
        self.oparl_base = f"{self.base_url}/api/v1/oparl"

    def _build_id_url(self, model_class: Type, obj_id: UUID) -> str:
        """Build the OParl ID (URL) for an object."""
        segment = OPARL_URL_SEGMENT[model_class]
        return f"{self.oparl_base}/{segment}/{obj_id}"

    async def get_system(self) -> dict | None:
        """Get the OParl System object."""
        result = await self.db.execute(select(System).limit(1))
        system = result.scalar_one_or_none()
        if not system:
            return None
        return self._serialize_system(system)

    async def get_object(self, model_class: Type, obj_id: UUID) -> dict | None:
        """Get a single OParl object by ID."""
        result = await self.db.execute(
            select(model_class).where(model_class.id == obj_id)
        )
        obj = result.scalar_one_or_none()
        if not obj or obj.deleted:
            return None
        return self._serialize(model_class, obj)

    async def list_objects(
        self,
        model_class: Type,
        page: int = 1,
        per_page: int = 25,
        **filters: Any,
    ) -> tuple[list[dict], int]:
        """List OParl objects with pagination and filtering."""
        query = select(model_class).where(model_class.deleted == False)

        # Apply filters
        for key, value in filters.items():
            if hasattr(model_class, key) and value is not None:
                query = query.where(getattr(model_class, key) == value)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Order by modified desc (newest first)
        if hasattr(model_class, "modified"):
            query = query.order_by(model_class.modified.desc())

        result = await self.db.execute(query)
        objects = result.scalars().all()

        return [self._serialize(model_class, obj) for obj in objects], total

    def _serialize(self, model_class: Type, obj: Any) -> dict:
        """Serialize a model object to OParl-compliant JSON."""
        serializers = {
            System: self._serialize_system,
            Body: self._serialize_body,
            LegislativeTerm: self._serialize_legislative_term,
            Organization: self._serialize_organization,
            Person: self._serialize_person,
            Membership: self._serialize_membership,
            Meeting: self._serialize_meeting,
            AgendaItem: self._serialize_agenda_item,
            Paper: self._serialize_paper,
            Consultation: self._serialize_consultation,
            File: self._serialize_file,
            Location: self._serialize_location,
        }
        serializer = serializers.get(model_class)
        if serializer:
            return serializer(obj)
        return self._serialize_generic(model_class, obj)

    def _base_fields(self, model_class: Type, obj: Any) -> dict:
        """Common OParl fields for all objects."""
        return {
            "id": self._build_id_url(model_class, obj.id),
            "type": OPARL_TYPE_MAP[model_class],
            "created": obj.created.isoformat() if obj.created else None,
            "modified": obj.modified.isoformat() if obj.modified else None,
            "deleted": obj.deleted,
            "keyword": obj.keyword or [],
            "web": obj.web,
            "license": obj.license,
        }

    def _serialize_system(self, obj: System) -> dict:
        return {
            **self._base_fields(System, obj),
            "oparlVersion": obj.oparl_version,
            "name": obj.name,
            "contactEmail": obj.contact_email,
            "contactName": obj.contact_name,
            "website": obj.website,
            "vendor": obj.vendor or "https://aitema.de",
            "product": obj.product or "https://aitema.de/ris",
            "otherOparlVersions": obj.other_oparl_versions or [],
            "body": f"{self.oparl_base}/body",
        }

    def _serialize_body(self, obj: Body) -> dict:
        return {
            **self._base_fields(Body, obj),
            "system": self._build_id_url(System, obj.system_id),
            "name": obj.name,
            "shortName": obj.short_name,
            "website": obj.website,
            "ags": obj.ags,
            "rgs": obj.rgs,
            "equivalent": obj.equivalent or [],
            "contactEmail": obj.contact_email,
            "contactName": obj.contact_name,
            "classification": obj.classification,
            "location": self._build_id_url(Location, obj.location_id) if obj.location_id else None,
            "organization": f"{self.oparl_base}/body/{obj.id}/organization",
            "person": f"{self.oparl_base}/body/{obj.id}/person",
            "meeting": f"{self.oparl_base}/body/{obj.id}/meeting",
            "paper": f"{self.oparl_base}/body/{obj.id}/paper",
            "legislativeTerm": f"{self.oparl_base}/body/{obj.id}/legislative-term",
        }

    def _serialize_legislative_term(self, obj: LegislativeTerm) -> dict:
        return {
            **self._base_fields(LegislativeTerm, obj),
            "body": self._build_id_url(Body, obj.body_id),
            "name": obj.name,
            "startDate": obj.start_date.isoformat() if obj.start_date else None,
            "endDate": obj.end_date.isoformat() if obj.end_date else None,
        }

    def _serialize_organization(self, obj: Organization) -> dict:
        return {
            **self._base_fields(Organization, obj),
            "body": self._build_id_url(Body, obj.body_id),
            "name": obj.name,
            "shortName": obj.short_name,
            "organizationType": obj.organization_type,
            "post": obj.post or [],
            "startDate": obj.start_date.isoformat() if obj.start_date else None,
            "endDate": obj.end_date.isoformat() if obj.end_date else None,
            "externalBody": obj.external_body,
            "website": obj.website,
            "classification": obj.classification,
            "location": self._build_id_url(Location, obj.location_id) if obj.location_id else None,
            "membership": f"{self.oparl_base}/organization/{obj.id}/membership",
            "meeting": [
                self._build_id_url(Meeting, m.id) for m in (obj.meetings or [])
            ],
        }

    def _serialize_person(self, obj: Person) -> dict:
        return {
            **self._base_fields(Person, obj),
            "body": self._build_id_url(Body, obj.body_id),
            "name": obj.name,
            "familyName": obj.family_name,
            "givenName": obj.given_name,
            "formOfAddress": obj.form_of_address,
            "affix": obj.affix,
            "title": obj.title or [],
            "gender": obj.gender,
            "phone": obj.phone or [],
            "email": obj.email or [],
            "streetAddress": obj.street_address,
            "postalCode": obj.postal_code,
            "locality": obj.locality,
            "status": obj.status or [],
            "life": obj.life,
            "lifeSource": obj.life_source,
            "location": self._build_id_url(Location, obj.location_id) if obj.location_id else None,
            "membership": [
                self._build_id_url(Membership, m.id) for m in (obj.memberships or [])
            ],
        }

    def _serialize_membership(self, obj: Membership) -> dict:
        return {
            **self._base_fields(Membership, obj),
            "person": self._build_id_url(Person, obj.person_id),
            "organization": self._build_id_url(Organization, obj.organization_id),
            "onBehalfOf": self._build_id_url(Organization, obj.on_behalf_of_id) if obj.on_behalf_of_id else None,
            "role": obj.role,
            "votingRight": obj.voting_right,
            "startDate": obj.start_date.isoformat() if obj.start_date else None,
            "endDate": obj.end_date.isoformat() if obj.end_date else None,
        }

    def _serialize_meeting(self, obj: Meeting) -> dict:
        return {
            **self._base_fields(Meeting, obj),
            "body": self._build_id_url(Body, obj.body_id),
            "name": obj.name,
            "meetingState": obj.meeting_state,
            "cancelled": obj.cancelled,
            "start": obj.start.isoformat() if obj.start else None,
            "end": obj.end.isoformat() if obj.end else None,
            "location": self._build_id_url(Location, obj.location_id) if obj.location_id else None,
            "organization": [
                self._build_id_url(Organization, o.id) for o in (obj.organization_list or [])
            ],
            "participant": [
                self._build_id_url(Person, p.id) for p in (obj.participants or [])
            ],
            "invitation": self._build_id_url(File, obj.invitation_id) if obj.invitation_id else None,
            "resultsProtocol": self._build_id_url(File, obj.results_protocol_id) if obj.results_protocol_id else None,
            "verbatimProtocol": self._build_id_url(File, obj.verbatim_protocol_id) if obj.verbatim_protocol_id else None,
            "auxiliaryFile": [
                self._build_id_url(File, f.id) for f in (obj.auxiliary_files or [])
            ],
            "agendaItem": [
                self._build_id_url(AgendaItem, a.id) for a in (obj.agenda_items or [])
            ],
        }

    def _serialize_agenda_item(self, obj: AgendaItem) -> dict:
        return {
            **self._base_fields(AgendaItem, obj),
            "meeting": self._build_id_url(Meeting, obj.meeting_id),
            "number": obj.number,
            "name": obj.name,
            "public": obj.public,
            "result": obj.result,
            "resolutionText": obj.resolution_text,
            "start": obj.start.isoformat() if obj.start else None,
            "end": obj.end.isoformat() if obj.end else None,
            "consultation": self._build_id_url(Consultation, obj.consultation_id) if obj.consultation_id else None,
            "resolutionFile": self._build_id_url(File, obj.result_file_id) if obj.result_file_id else None,
            "auxiliaryFile": [
                self._build_id_url(File, f.id) for f in (obj.auxiliary_files or [])
            ],
        }

    def _serialize_paper(self, obj: Paper) -> dict:
        return {
            **self._base_fields(Paper, obj),
            "body": self._build_id_url(Body, obj.body_id),
            "name": obj.name,
            "reference": obj.reference,
            "date": obj.date.isoformat() if obj.date else None,
            "paperType": obj.paper_type,
            "mainFile": self._build_id_url(File, obj.main_file_id) if obj.main_file_id else None,
            "auxiliaryFile": [
                self._build_id_url(File, f.id) for f in (obj.auxiliary_files or [])
            ],
            "originatorPerson": [
                self._build_id_url(Person, p.id) for p in (obj.originator_persons or [])
            ],
            "originatorOrganization": [
                self._build_id_url(Organization, o.id) for o in (obj.originator_organizations or [])
            ],
            "underDirectionOf": [
                self._build_id_url(Organization, o.id) for o in (obj.under_direction_of or [])
            ],
            "consultation": f"{self.oparl_base}/paper/{obj.id}/consultation",
            "location": [
                self._build_id_url(Location, l.id) for l in (obj.locations or [])
            ],
        }

    def _serialize_consultation(self, obj: Consultation) -> dict:
        return {
            **self._base_fields(Consultation, obj),
            "paper": self._build_id_url(Paper, obj.paper_id),
            "meeting": self._build_id_url(Meeting, obj.meeting_id) if obj.meeting_id else None,
            "authoritative": obj.authoritative,
            "role": obj.role,
            "organization": [
                self._build_id_url(Organization, o.id) for o in (obj.organizations or [])
            ],
            "agendaItem": [
                self._build_id_url(AgendaItem, a.id) for a in (obj.agenda_items or [])
            ],
        }

    def _serialize_file(self, obj: File) -> dict:
        return {
            **self._base_fields(File, obj),
            "name": obj.name,
            "fileName": obj.file_name,
            "mimeType": obj.mime_type,
            "date": obj.date.isoformat() if obj.date else None,
            "size": obj.size,
            "sha1Checksum": obj.sha1_checksum,
            "sha512Checksum": obj.sha512_checksum,
            "text": obj.text,
            "accessUrl": obj.access_url or f"{self.oparl_base}/file/{obj.id}/access",
            "externalServiceUrl": obj.external_service_url,
            "downloadUrl": obj.download_url or f"{self.oparl_base}/file/{obj.id}/download",
            "fileLicense": obj.file_license,
        }

    def _serialize_location(self, obj: Location) -> dict:
        return {
            **self._base_fields(Location, obj),
            "description": obj.description,
            "streetAddress": obj.street_address,
            "room": obj.room,
            "postalCode": obj.postal_code,
            "locality": obj.locality,
            "subLocality": obj.sub_locality,
            "geojson": obj.geojson,
        }

    def _serialize_generic(self, model_class: Type, obj: Any) -> dict:
        """Fallback serializer for unknown types."""
        result = self._base_fields(model_class, obj)
        for col in obj.__table__.columns:
            if col.name not in result:
                val = getattr(obj, col.name, None)
                if hasattr(val, "isoformat"):
                    val = val.isoformat()
                result[col.name] = val
        return result
