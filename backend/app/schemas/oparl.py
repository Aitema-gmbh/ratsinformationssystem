"""
OParl 1.1 Pydantic Schemas for API serialization.
"""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class OParlBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    type: str = ""
    name: Optional[str] = None
    short_name: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    deleted: bool = False
    keyword: List[str] = []
    web: Optional[str] = None
    license: Optional[str] = None


class SystemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    type: str = "https://schema.oparl.org/1.1/System"
    oparl_version: str = "https://schema.oparl.org/1.1/"
    name: str
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    vendor: Optional[str] = None
    product: Optional[str] = None
    body: str = ""  # URL to bodies list
    other_oparl_versions: List[str] = []


class BodySchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Body"
    system: Optional[str] = None  # URL
    body_type: Optional[str] = None
    classification: Optional[str] = None
    equivalent_body: List[str] = []
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    ags: Optional[str] = None
    rgs: Optional[str] = None
    organization: str = ""  # URL to list
    person: str = ""
    meeting: str = ""
    paper: str = ""
    legislative_term: str = ""


class BodyListSchema(BaseModel):
    data: List[BodySchema]
    pagination: dict = {}
    links: dict = {}


class OrganizationSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Organization"
    body: Optional[str] = None
    organization_type: Optional[str] = None
    classification: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    membership: List[str] = []
    location: Optional[str] = None
    external_body: Optional[str] = None


class PersonSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Person"
    body: Optional[str] = None
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    form_of_address: Optional[str] = None
    affix: Optional[str] = None
    title: List[str] = []
    gender: Optional[str] = None
    phone: List[str] = []
    email: List[str] = []
    status: List[str] = []
    membership: List[str] = []
    life: Optional[str] = None
    life_source: Optional[str] = None
    location: Optional[str] = None


class MembershipSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Membership"
    person: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    voting_right: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    on_behalf_of: Optional[str] = None


class LocationSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Location"
    description: Optional[str] = None
    street_address: Optional[str] = None
    room: Optional[str] = None
    postal_code: Optional[str] = None
    sub_locality: Optional[str] = None
    locality: Optional[str] = None
    geojson: Optional[dict] = None


class MeetingSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Meeting"
    meeting_state: Optional[str] = None
    cancelled: bool = False
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = None
    organization: Optional[str] = None
    participant: List[str] = []
    invitation: Optional[str] = None
    results_protocol: Optional[str] = None
    verbatim_protocol: Optional[str] = None
    agenda_item: List[str] = []


class AgendaItemSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/AgendaItem"
    meeting: Optional[str] = None
    number: Optional[str] = None
    order: int = 0
    public: bool = True
    result: Optional[str] = None
    resolution_text: Optional[str] = None
    resolution_file: Optional[str] = None
    consultation: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class PaperSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Paper"
    body: Optional[str] = None
    reference: Optional[str] = None
    date: Optional[date] = None
    paper_type: Optional[str] = None
    main_file: Optional[str] = None
    auxiliary_file: List[str] = []
    originator_person: List[str] = []
    originator_organization: List[str] = []
    consultation: List[str] = []


class ConsultationSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/Consultation"
    paper: Optional[str] = None
    agenda_item: Optional[str] = None
    organization: Optional[str] = None
    authoritative: bool = False
    role: Optional[str] = None


class FileSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/File"
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    sha512_checksum: Optional[str] = None
    text: Optional[str] = None
    access_url: Optional[str] = None
    download_url: Optional[str] = None
    external_service_url: Optional[str] = None
    master_file: Optional[str] = None


class LegislativeTermSchema(OParlBase):
    type: str = "https://schema.oparl.org/1.1/LegislativeTerm"
    body: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Pagination schema
class PaginatedResponse(BaseModel):
    data: List[Any] = []
    pagination: dict = Field(default_factory=lambda: {
        "totalElements": 0,
        "elementsPerPage": 100,
        "currentPage": 1,
        "totalPages": 1,
    })
    links: dict = Field(default_factory=lambda: {
        "first": "",
        "last": "",
        "next": None,
        "prev": None,
    })
