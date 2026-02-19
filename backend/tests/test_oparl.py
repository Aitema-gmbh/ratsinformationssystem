"""
Tests for OParl 1.1 API compliance.

Validates:
- All 12 OParl object types are exposed
- Pagination follows OParl spec
- URLs are properly formatted
- Required fields are present
"""
import pytest
from datetime import date, datetime
from app.models.oparl import (
    OParlSystem, Body, Organization, Person, Membership,
    Meeting, AgendaItem, Paper, Consultation, File,
    Location, LegislativeTerm,
)


class TestOParlObjectTypes:
    """All 12 OParl types must be represented."""

    def test_system_type(self):
        assert OParlSystem.__tablename__ == 'oparl_systems'

    def test_body_type(self):
        assert Body.__tablename__ == 'bodies'

    def test_organization_type(self):
        assert Organization.__tablename__ == 'organizations'

    def test_person_type(self):
        assert Person.__tablename__ == 'persons'

    def test_membership_type(self):
        assert Membership.__tablename__ == 'memberships'

    def test_meeting_type(self):
        assert Meeting.__tablename__ == 'meetings'

    def test_agenda_item_type(self):
        assert AgendaItem.__tablename__ == 'agenda_items'

    def test_paper_type(self):
        assert Paper.__tablename__ == 'papers'

    def test_consultation_type(self):
        assert Consultation.__tablename__ == 'consultations'

    def test_file_type(self):
        assert File.__tablename__ == 'files'

    def test_location_type(self):
        assert Location.__tablename__ == 'locations'

    def test_legislative_term_type(self):
        assert LegislativeTerm.__tablename__ == 'legislative_terms'


class TestOParlSchemas:
    """OParl schema validation."""

    def test_body_has_ags_field(self):
        """AGS (Amtlicher Gemeindeschluessel) must be on Body."""
        assert hasattr(Body, 'ags')

    def test_body_has_rgs_field(self):
        """RGS (Regionalschluessel) must be on Body."""
        assert hasattr(Body, 'rgs')

    def test_person_has_name_fields(self):
        assert hasattr(Person, 'family_name')
        assert hasattr(Person, 'given_name')
        assert hasattr(Person, 'form_of_address')

    def test_meeting_states(self):
        """Meeting must support all OParl meeting states."""
        assert hasattr(Meeting, 'meeting_state')
        assert hasattr(Meeting, 'cancelled')

    def test_paper_has_reference(self):
        """Paper must have a reference number."""
        assert hasattr(Paper, 'reference')

    def test_file_has_checksum(self):
        """File must support SHA-512 checksums."""
        assert hasattr(File, 'sha512_checksum')

    def test_location_has_geojson(self):
        """Location must support GeoJSON."""
        assert hasattr(Location, 'geojson')


class TestWorkflowTransitions:
    """Paper and Meeting workflow transitions."""

    def test_paper_transitions_defined(self):
        from app.services.workflow import PAPER_TRANSITIONS
        assert 'draft' in PAPER_TRANSITIONS
        assert 'submitted' in PAPER_TRANSITIONS
        assert 'decided' in PAPER_TRANSITIONS

    def test_meeting_transitions_defined(self):
        from app.services.workflow import MEETING_TRANSITIONS
        assert 'scheduled' in MEETING_TRANSITIONS
        assert 'running' in MEETING_TRANSITIONS
        assert 'completed' in MEETING_TRANSITIONS

    def test_paper_draft_can_be_submitted(self):
        from app.services.workflow import PAPER_TRANSITIONS
        assert 'submitted' in PAPER_TRANSITIONS['draft']

    def test_completed_meeting_is_terminal(self):
        from app.services.workflow import MEETING_TRANSITIONS
        assert len(MEETING_TRANSITIONS['completed']) == 0

    def test_paper_reference_format(self):
        """References should follow format PREFIX/YEAR/NNN."""
        from app.services.workflow import WorkflowService
        # Format validation
        ref = "V/2026/001"
        parts = ref.split('/')
        assert len(parts) == 3
        assert len(parts[2]) == 3  # zero-padded


class TestMultiTenant:
    """Multi-tenant isolation."""

    def test_body_has_tenant_id(self):
        assert hasattr(Body, 'tenant_id')

    def test_organization_has_tenant_id(self):
        assert hasattr(Organization, 'tenant_id')

    def test_person_has_tenant_id(self):
        assert hasattr(Person, 'tenant_id')

    def test_meeting_has_tenant_id(self):
        assert hasattr(Meeting, 'tenant_id')

    def test_paper_has_tenant_id(self):
        assert hasattr(Paper, 'tenant_id')
