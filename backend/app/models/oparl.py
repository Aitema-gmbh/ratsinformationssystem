"""
OParl 1.1 Data Models for aitema|Rats

Implements all 12 OParl object types as SQLAlchemy models:
https://oparl.org/spezifikation/online-ansicht/

Object Types:
1. System - API entry point
2. Body - Koerperschaft (Kommune, Kreis)
3. Organization - Fraktion, Ausschuss, Partei
4. Person - Mandatstraeger, Mitarbeiter
5. Membership - Zugehoerigkeit Person <-> Organization
6. Meeting - Sitzung
7. AgendaItem - Tagesordnungspunkt
8. Paper - Vorlage, Drucksache
9. Consultation - Beratung (Paper <-> Meeting)
10. File - Dokument/Datei
11. Location - Ort
12. LegislativeTerm - Wahlperiode
"""
import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, Table, JSON, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    """Common timestamp fields for all OParl objects."""
    created = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    modified = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OParlMixin(TimestampMixin):
    """Common OParl object fields."""
    id = mapped_column(String(36), primary_key=True, default=generate_uuid)
    oparl_id = mapped_column(String(512), unique=True, nullable=True, comment="External OParl ID URL")
    name = mapped_column(String(512), nullable=True)
    short_name = mapped_column(String(128), nullable=True)
    deleted = mapped_column(Boolean, default=False, nullable=False)
    keyword = mapped_column(ARRAY(String), default=list, nullable=True)
    web = mapped_column(String(1024), nullable=True)
    license = mapped_column(String(512), nullable=True)

    # Multi-tenant
    tenant_id = mapped_column(String(36), nullable=False, index=True)


# Association tables
paper_originator_person = Table(
    'paper_originator_person', Base.metadata,
    Column('paper_id', String(36), ForeignKey('papers.id')),
    Column('person_id', String(36), ForeignKey('persons.id')),
)

paper_originator_org = Table(
    'paper_originator_org', Base.metadata,
    Column('paper_id', String(36), ForeignKey('papers.id')),
    Column('organization_id', String(36), ForeignKey('organizations.id')),
)

meeting_participant = Table(
    'meeting_participant', Base.metadata,
    Column('meeting_id', String(36), ForeignKey('meetings.id')),
    Column('person_id', String(36), ForeignKey('persons.id')),
)

paper_file = Table(
    'paper_file', Base.metadata,
    Column('paper_id', String(36), ForeignKey('papers.id')),
    Column('file_id', String(36), ForeignKey('files.id')),
)


class OParlSystem(Base, TimestampMixin):
    """OParl:System - API Entry Point."""
    __tablename__ = 'oparl_systems'

    id = mapped_column(String(36), primary_key=True, default=generate_uuid)
    oparl_version = mapped_column(String(64), default='https://schema.oparl.org/1.1/', nullable=False)
    name = mapped_column(String(256), nullable=False)
    website = mapped_column(String(1024), nullable=True)
    contact_email = mapped_column(String(256), nullable=True)
    contact_name = mapped_column(String(256), nullable=True)
    vendor = mapped_column(String(512), default='https://aitema.de', nullable=True)
    product = mapped_column(String(512), default='https://github.com/aitema/ratsinformationssystem', nullable=True)
    other_oparl_versions = mapped_column(ARRAY(String), default=list, nullable=True)

    # Relationships
    bodies = relationship('Body', back_populates='system', lazy='dynamic')


class Body(Base, OParlMixin):
    """OParl:Body - Koerperschaft (Kommune, Kreis, etc.)."""
    __tablename__ = 'bodies'

    system_id = mapped_column(String(36), ForeignKey('oparl_systems.id'), nullable=False)
    body_type = mapped_column(String(128), nullable=True, comment="z.B. Gemeinde, Stadt, Kreis")
    classification = mapped_column(String(256), nullable=True)
    equivalent_body = mapped_column(ARRAY(String), default=list, nullable=True)
    contact_email = mapped_column(String(256), nullable=True)
    contact_name = mapped_column(String(256), nullable=True)
    ags = mapped_column(String(12), nullable=True, comment="Amtlicher Gemeindeschluessel")
    rgs = mapped_column(String(12), nullable=True, comment="Regionalschluessel")

    # Relationships
    system = relationship('OParlSystem', back_populates='bodies')
    organizations = relationship('Organization', back_populates='body', lazy='dynamic')
    persons = relationship('Person', back_populates='body', lazy='dynamic')
    meetings = relationship('Meeting', back_populates='body', lazy='dynamic')
    papers = relationship('Paper', back_populates='body', lazy='dynamic')
    legislative_terms = relationship('LegislativeTerm', back_populates='body', lazy='dynamic')
    locations = relationship('Location', back_populates='body', lazy='dynamic')

    __table_args__ = (
        Index('ix_bodies_tenant_ags', 'tenant_id', 'ags'),
    )


class LegislativeTerm(Base, OParlMixin):
    """OParl:LegislativeTerm - Wahlperiode."""
    __tablename__ = 'legislative_terms'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=False)
    start_date = mapped_column(Date, nullable=True)
    end_date = mapped_column(Date, nullable=True)

    body = relationship('Body', back_populates='legislative_terms')


class Organization(Base, OParlMixin):
    """OParl:Organization - Fraktion, Ausschuss, Partei, Verwaltung."""
    __tablename__ = 'organizations'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=False)
    organization_type = mapped_column(
        String(64), nullable=True,
        comment="fraktion, ausschuss, partei, verwaltung, sonstiges"
    )
    classification = mapped_column(String(256), nullable=True)
    start_date = mapped_column(Date, nullable=True)
    end_date = mapped_column(Date, nullable=True)
    location_id = mapped_column(String(36), ForeignKey('locations.id'), nullable=True)
    external_body_id = mapped_column(String(36), nullable=True, comment="Ref to another Body")

    body = relationship('Body', back_populates='organizations')
    memberships = relationship('Membership', back_populates='organization', lazy='dynamic')
    location = relationship('Location', foreign_keys=[location_id])

    __table_args__ = (
        Index('ix_org_body_type', 'body_id', 'organization_type'),
    )


class Person(Base, OParlMixin):
    """OParl:Person - Mandatstraeger oder andere Person."""
    __tablename__ = 'persons'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=False)
    family_name = mapped_column(String(256), nullable=True)
    given_name = mapped_column(String(256), nullable=True)
    form_of_address = mapped_column(String(64), nullable=True, comment="Herr, Frau, Dr., etc.")
    affix = mapped_column(String(64), nullable=True, comment="von, zu, etc.")
    title = mapped_column(ARRAY(String), default=list, nullable=True)
    gender = mapped_column(String(32), nullable=True)
    phone = mapped_column(ARRAY(String), default=list, nullable=True)
    email = mapped_column(ARRAY(String), default=list, nullable=True)
    status = mapped_column(ARRAY(String), default=list, nullable=True)
    life = mapped_column(Text, nullable=True)
    life_source = mapped_column(String(1024), nullable=True)
    location_id = mapped_column(String(36), ForeignKey('locations.id'), nullable=True)

    body = relationship('Body', back_populates='persons')
    memberships = relationship('Membership', back_populates='person', lazy='dynamic')
    location = relationship('Location', foreign_keys=[location_id])

    @hybrid_property
    def display_name(self):
        parts = []
        if self.form_of_address:
            parts.append(self.form_of_address)
        if self.given_name:
            parts.append(self.given_name)
        if self.affix:
            parts.append(self.affix)
        if self.family_name:
            parts.append(self.family_name)
        return ' '.join(parts) if parts else self.name or 'Unbekannt'


class Membership(Base, OParlMixin):
    """OParl:Membership - Mitgliedschaft Person in Organization."""
    __tablename__ = 'memberships'

    person_id = mapped_column(String(36), ForeignKey('persons.id'), nullable=False)
    organization_id = mapped_column(String(36), ForeignKey('organizations.id'), nullable=False)
    role = mapped_column(String(128), nullable=True, comment="Vorsitzende/r, Mitglied, etc.")
    voting_right = mapped_column(Boolean, default=True, nullable=False)
    start_date = mapped_column(Date, nullable=True)
    end_date = mapped_column(Date, nullable=True)
    on_behalf_of_id = mapped_column(String(36), ForeignKey('organizations.id'), nullable=True)

    person = relationship('Person', back_populates='memberships')
    organization = relationship('Organization', back_populates='memberships', foreign_keys=[organization_id])
    on_behalf_of = relationship('Organization', foreign_keys=[on_behalf_of_id])

    __table_args__ = (
        Index('ix_membership_person_org', 'person_id', 'organization_id'),
    )


class Location(Base, OParlMixin):
    """OParl:Location - Ortsangabe."""
    __tablename__ = 'locations'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=True)
    description = mapped_column(Text, nullable=True)
    street_address = mapped_column(String(512), nullable=True)
    room = mapped_column(String(256), nullable=True)
    postal_code = mapped_column(String(16), nullable=True)
    sub_locality = mapped_column(String(256), nullable=True)
    locality = mapped_column(String(256), nullable=True)
    geojson = mapped_column(JSONB, nullable=True, comment="GeoJSON geometry")

    body = relationship('Body', back_populates='locations')


class Meeting(Base, OParlMixin):
    """OParl:Meeting - Sitzung."""
    __tablename__ = 'meetings'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=False)
    meeting_state = mapped_column(
        String(32), default='scheduled', nullable=False,
        comment="scheduled, invited, running, completed, cancelled"
    )
    cancelled = mapped_column(Boolean, default=False, nullable=False)
    start = mapped_column(DateTime, nullable=True)
    end = mapped_column(DateTime, nullable=True)
    location_id = mapped_column(String(36), ForeignKey('locations.id'), nullable=True)
    invitation_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)
    results_protocol_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)
    verbatim_protocol_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)

    body = relationship('Body', back_populates='meetings')
    location = relationship('Location', foreign_keys=[location_id])
    invitation = relationship('File', foreign_keys=[invitation_id])
    results_protocol = relationship('File', foreign_keys=[results_protocol_id])
    verbatim_protocol = relationship('File', foreign_keys=[verbatim_protocol_id])
    agenda_items = relationship('AgendaItem', back_populates='meeting', order_by='AgendaItem.order')
    participants = relationship('Person', secondary=meeting_participant, lazy='dynamic')
    organization_id = mapped_column(String(36), ForeignKey('organizations.id'), nullable=True)
    organization = relationship('Organization', foreign_keys=[organization_id])

    __table_args__ = (
        Index('ix_meeting_body_state', 'body_id', 'meeting_state'),
        Index('ix_meeting_start', 'start'),
    )


class AgendaItem(Base, OParlMixin):
    """OParl:AgendaItem - Tagesordnungspunkt."""
    __tablename__ = 'agenda_items'

    meeting_id = mapped_column(String(36), ForeignKey('meetings.id'), nullable=False)
    number = mapped_column(String(32), nullable=True, comment="TOP-Nummer")
    order = mapped_column(Integer, default=0, nullable=False)
    public = mapped_column(Boolean, default=True, nullable=False)
    result = mapped_column(Text, nullable=True)
    resolution_text = mapped_column(Text, nullable=True)
    resolution_file_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)
    start = mapped_column(DateTime, nullable=True)
    end = mapped_column(DateTime, nullable=True)

    meeting = relationship('Meeting', back_populates='agenda_items')
    consultation = relationship('Consultation', back_populates='agenda_item', uselist=False)
    resolution_file = relationship('File', foreign_keys=[resolution_file_id])


class Paper(Base, OParlMixin):
    """OParl:Paper - Drucksache / Vorlage."""
    __tablename__ = 'papers'

    body_id = mapped_column(String(36), ForeignKey('bodies.id'), nullable=False)
    reference = mapped_column(String(128), nullable=True, comment="Drucksachennummer")
    date = mapped_column(Date, nullable=True)
    paper_type = mapped_column(String(128), nullable=True, comment="Vorlage, Antrag, Anfrage, etc.")
    main_file_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)
    simple_language_text = mapped_column(Text, nullable=True, comment="KI-generierte einfache Sprache (A2)")
    simple_language_generated_at = mapped_column(DateTime, nullable=True)

    body = relationship('Body', back_populates='papers')
    main_file = relationship('File', foreign_keys=[main_file_id])
    auxiliary_files = relationship('File', secondary=paper_file, lazy='dynamic')
    consultations = relationship('Consultation', back_populates='paper', lazy='dynamic')
    originator_persons = relationship('Person', secondary=paper_originator_person, lazy='dynamic')
    originator_organizations = relationship('Organization', secondary=paper_originator_org, lazy='dynamic')

    __table_args__ = (
        Index('ix_paper_body_ref', 'body_id', 'reference'),
        Index('ix_paper_date', 'date'),
    )


class Consultation(Base, OParlMixin):
    """OParl:Consultation - Beratung einer Drucksache in einer Sitzung."""
    __tablename__ = 'consultations'

    paper_id = mapped_column(String(36), ForeignKey('papers.id'), nullable=False)
    agenda_item_id = mapped_column(String(36), ForeignKey('agenda_items.id'), nullable=True)
    organization_id = mapped_column(String(36), ForeignKey('organizations.id'), nullable=True)
    authoritative = mapped_column(Boolean, default=False, nullable=False, comment="Federfuehrende Beratung")
    role = mapped_column(String(128), nullable=True, comment="Rolle des Gremiums")

    paper = relationship('Paper', back_populates='consultations')
    agenda_item = relationship('AgendaItem', back_populates='consultation')
    organization = relationship('Organization', foreign_keys=[organization_id])


class File(Base, OParlMixin):
    """OParl:File - Datei / Dokument."""
    __tablename__ = 'files'

    file_name = mapped_column(String(512), nullable=True)
    mime_type = mapped_column(String(128), nullable=True)
    size = mapped_column(Integer, nullable=True, comment="Dateigroesse in Bytes")
    sha512_checksum = mapped_column(String(128), nullable=True)
    text = mapped_column(Text, nullable=True, comment="Extrahierter Volltext")
    access_url = mapped_column(String(1024), nullable=True)
    download_url = mapped_column(String(1024), nullable=True)
    external_service_url = mapped_column(String(1024), nullable=True)
    master_file_id = mapped_column(String(36), ForeignKey('files.id'), nullable=True)

    # Storage
    storage_path = mapped_column(String(1024), nullable=True, comment="Pfad im Object Storage")

    master_file = relationship('File', remote_side='File.id')

    __table_args__ = (
        Index('ix_file_mime', 'mime_type'),
    )
