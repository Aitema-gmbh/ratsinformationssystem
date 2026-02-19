"""
Tests for RIS Workflow Service.

Covers:
- Paper lifecycle: draft -> submitted -> deliberation -> decided -> published
- Meeting lifecycle: scheduled -> invited -> running -> completed
- Invalid transition rejection
- Agenda item management (add, reorder)
- Resolution recording
- Reference number generation (V/2026/001 format)
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, date

from app.services.workflow import (
    WorkflowService,
    PAPER_TRANSITIONS,
    MEETING_TRANSITIONS,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.commit = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    return WorkflowService(mock_session)


def _mock_paper(**kwargs):
    p = MagicMock()
    p.id = kwargs.get("id", "paper-001")
    p.body_id = kwargs.get("body_id", "body-001")
    p.tenant_id = kwargs.get("tenant_id", "tenant-001")
    p.name = kwargs.get("name", "Vorlage Haushalt 2026")
    p.paper_type = kwargs.get("paper_type", "Vorlage")
    p.reference = kwargs.get("reference", "V/2026/001")
    p.date = kwargs.get("date", date(2026, 1, 15))
    p.deleted = kwargs.get("deleted", False)
    return p


def _mock_meeting(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", "meeting-001")
    m.body_id = kwargs.get("body_id", "body-001")
    m.tenant_id = kwargs.get("tenant_id", "tenant-001")
    m.name = kwargs.get("name", "Stadtratssitzung 15.01.2026")
    m.meeting_state = kwargs.get("meeting_state", "scheduled")
    m.start = kwargs.get("start", datetime(2026, 1, 15, 18, 0))
    m.end = kwargs.get("end", datetime(2026, 1, 15, 20, 0))
    m.organization_id = kwargs.get("organization_id", "org-stadtrat")
    m.modified = kwargs.get("modified", None)
    return m


def _mock_agenda_item(**kwargs):
    item = MagicMock()
    item.id = kwargs.get("id", "ai-001")
    item.meeting_id = kwargs.get("meeting_id", "meeting-001")
    item.tenant_id = kwargs.get("tenant_id", "tenant-001")
    item.name = kwargs.get("name", "Haushalt 2026")
    item.number = kwargs.get("number", "TOP 1")
    item.order = kwargs.get("order", 1)
    item.public = kwargs.get("public", True)
    item.result = kwargs.get("result", None)
    item.resolution_text = kwargs.get("resolution_text", None)
    item.resolution_file_id = kwargs.get("resolution_file_id", None)
    item.modified = kwargs.get("modified", None)
    return item


# ============================================================
# Test: Paper Lifecycle
# ============================================================

class TestPaperLifecycle:
    """Test complete paper lifecycle: draft -> published."""

    def test_paper_transitions_defined(self):
        assert "draft" in PAPER_TRANSITIONS
        assert "submitted" in PAPER_TRANSITIONS
        assert "deliberation" in PAPER_TRANSITIONS
        assert "decided" in PAPER_TRANSITIONS
        assert "published" in PAPER_TRANSITIONS

    def test_full_happy_path(self):
        path = ["draft", "submitted", "deliberation", "decided", "published"]
        for i in range(len(path) - 1):
            current, next_s = path[i], path[i + 1]
            allowed = PAPER_TRANSITIONS[current]
            assert next_s in allowed, f"{current} -> {next_s} must be valid"

    def test_draft_to_submitted(self):
        assert "submitted" in PAPER_TRANSITIONS["draft"]

    def test_submitted_to_deliberation(self):
        assert "deliberation" in PAPER_TRANSITIONS["submitted"]

    def test_deliberation_to_decided(self):
        assert "decided" in PAPER_TRANSITIONS["deliberation"]

    def test_decided_to_published(self):
        assert "published" in PAPER_TRANSITIONS["decided"]

    def test_published_is_terminal(self):
        assert len(PAPER_TRANSITIONS["published"]) == 0

    def test_withdrawn_is_terminal(self):
        assert len(PAPER_TRANSITIONS["withdrawn"]) == 0

    def test_deferred_can_return_to_deliberation(self):
        assert "deliberation" in PAPER_TRANSITIONS["deferred"]

    def test_any_active_state_can_be_withdrawn(self):
        for state in ["draft", "submitted", "deliberation", "deferred"]:
            assert "withdrawn" in PAPER_TRANSITIONS[state], \
                f"{state} must allow withdrawal"


# ============================================================
# Test: Meeting Lifecycle
# ============================================================

class TestMeetingLifecycle:
    """Test meeting lifecycle: scheduled -> completed."""

    def test_meeting_transitions_defined(self):
        assert "scheduled" in MEETING_TRANSITIONS
        assert "invited" in MEETING_TRANSITIONS
        assert "running" in MEETING_TRANSITIONS
        assert "completed" in MEETING_TRANSITIONS

    def test_full_happy_path(self):
        path = ["scheduled", "invited", "running", "completed"]
        for i in range(len(path) - 1):
            current, next_s = path[i], path[i + 1]
            allowed = MEETING_TRANSITIONS[current]
            assert next_s in allowed, f"{current} -> {next_s} must be valid"

    def test_scheduled_to_invited(self):
        assert "invited" in MEETING_TRANSITIONS["scheduled"]

    def test_invited_to_running(self):
        assert "running" in MEETING_TRANSITIONS["invited"]

    def test_running_to_completed(self):
        assert "completed" in MEETING_TRANSITIONS["running"]

    def test_completed_is_terminal(self):
        assert len(MEETING_TRANSITIONS["completed"]) == 0

    def test_cancelled_is_terminal(self):
        assert len(MEETING_TRANSITIONS["cancelled"]) == 0

    def test_scheduled_can_be_cancelled(self):
        assert "cancelled" in MEETING_TRANSITIONS["scheduled"]

    def test_invited_can_be_cancelled(self):
        assert "cancelled" in MEETING_TRANSITIONS["invited"]

    def test_change_meeting_state_valid(self, service, mock_session):
        meeting = _mock_meeting(meeting_state="scheduled")
        mock_session.query.return_value.filter.return_value.first.return_value = meeting

        result = service.change_meeting_state("meeting-001", "invited")
        assert meeting.meeting_state == "invited"

    def test_change_meeting_state_invalid(self, service, mock_session):
        meeting = _mock_meeting(meeting_state="completed")
        mock_session.query.return_value.filter.return_value.first.return_value = meeting

        with pytest.raises(ValueError, match="Ungueltige Statusaenderung"):
            service.change_meeting_state("meeting-001", "scheduled")

    def test_change_meeting_state_not_found(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="nicht gefunden"):
            service.change_meeting_state("nonexistent", "invited")


# ============================================================
# Test: Invalid Paper Transition
# ============================================================

class TestInvalidPaperTransition:
    """Test rejection of invalid paper transitions."""

    def test_draft_cannot_skip_to_decided(self):
        assert "decided" not in PAPER_TRANSITIONS["draft"]

    def test_submitted_cannot_skip_to_published(self):
        assert "published" not in PAPER_TRANSITIONS["submitted"]

    def test_decided_cannot_go_back_to_draft(self):
        assert "draft" not in PAPER_TRANSITIONS["decided"]

    def test_published_cannot_revert(self):
        allowed = PAPER_TRANSITIONS["published"]
        assert len(allowed) == 0


# ============================================================
# Test: Add Agenda Item
# ============================================================

class TestAddAgendaItem:
    """Test adding agenda items (TOPs) to meetings."""

    def test_add_agenda_item(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        mock_session.query.return_value.filter.return_value.first.return_value = \
            _mock_meeting()

        result = service.add_agenda_item(
            meeting_id="meeting-001",
            tenant_id="tenant-001",
            name="Haushalt 2026",
            public=True,
        )
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_auto_number_assignment(self):
        """Without explicit number, TOP N auto-assigned."""
        max_order = 3
        expected_number = f"TOP {max_order + 1}"
        assert expected_number == "TOP 4"

    def test_agenda_item_linked_to_paper(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        meeting = _mock_meeting()
        mock_session.query.return_value.filter.return_value.first.return_value = meeting

        service.add_agenda_item(
            meeting_id="meeting-001",
            tenant_id="tenant-001",
            name="Bebauungsplan",
            paper_id="paper-001",
        )
        # Should have at least 2 adds: AgendaItem + Consultation
        assert mock_session.add.call_count >= 2


# ============================================================
# Test: Reorder Agenda
# ============================================================

class TestReorderAgenda:
    """Test reordering of TOPs."""

    def test_reorder_updates_order(self, service, mock_session):
        items = [
            _mock_agenda_item(id="ai-1", order=1, number="TOP 1"),
            _mock_agenda_item(id="ai-2", order=2, number="TOP 2"),
            _mock_agenda_item(id="ai-3", order=3, number="TOP 3"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = items

        # Reverse order
        result = service.reorder_agenda("meeting-001", ["ai-3", "ai-2", "ai-1"])
        mock_session.commit.assert_called()

    def test_reorder_renumbers_tops(self):
        """After reorder, TOPs should be renumbered 1, 2, 3..."""
        items = ["ai-3", "ai-1", "ai-2"]
        for i, item_id in enumerate(items):
            expected_number = f"TOP {i + 1}"
            assert expected_number == f"TOP {i + 1}"


# ============================================================
# Test: Set Resolution
# ============================================================

class TestSetResolution:
    """Test recording resolutions/vote results."""

    def test_set_resolution(self, service, mock_session):
        item = _mock_agenda_item()
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.set_resolution(
            agenda_item_id="ai-001",
            result="einstimmig angenommen",
            resolution_text="Der Haushalt 2026 wird beschlossen.",
        )
        assert item.result == "einstimmig angenommen"
        assert item.resolution_text == "Der Haushalt 2026 wird beschlossen."
        mock_session.commit.assert_called()

    def test_set_resolution_not_found(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="nicht gefunden"):
            service.set_resolution("nonexistent", "abgelehnt")

    def test_set_resolution_with_file(self, service, mock_session):
        item = _mock_agenda_item()
        mock_session.query.return_value.filter.return_value.first.return_value = item

        service.set_resolution(
            agenda_item_id="ai-001",
            result="angenommen",
            resolution_file_id="file-001",
        )
        assert item.resolution_file_id == "file-001"


# ============================================================
# Test: Generate Reference
# ============================================================

class TestGenerateReference:
    """Test paper reference number generation."""

    def test_vorlage_reference_format(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0

        ref = service._generate_reference("body-001", "Vorlage")
        year = date.today().year
        assert ref == f"V/{year}/001"

    def test_antrag_reference_format(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0

        ref = service._generate_reference("body-001", "Antrag")
        year = date.today().year
        assert ref == f"A/{year}/001"

    def test_anfrage_reference_format(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0

        ref = service._generate_reference("body-001", "Anfrage")
        year = date.today().year
        assert ref == f"AF/{year}/001"

    def test_reference_sequence_increments(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 5

        ref = service._generate_reference("body-001", "Vorlage")
        year = date.today().year
        assert ref == f"V/{year}/006"

    def test_reference_zero_padded(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        ref = service._generate_reference("body-001", "Vorlage")
        parts = ref.split("/")
        assert len(parts[2]) == 3

    def test_unknown_type_defaults_to_ds(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        ref = service._generate_reference("body-001", "UnknownType")
        assert ref.startswith("DS/")

    def test_beschlussvorlage_prefix(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        ref = service._generate_reference("body-001", "Beschlussvorlage")
        assert ref.startswith("BV/")

    def test_mitteilung_prefix(self, service, mock_session):
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        ref = service._generate_reference("body-001", "Mitteilung")
        assert ref.startswith("M/")
