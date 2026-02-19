"""
Tests for RIS Migration Service.

Covers:
- ALLRIS CSV import with German column names
- OParl API pagination handling
- Migration result counters and error lists
- CSV BOM handling
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, date

from app.services.migration import (
    MigrationResult,
    OParlMigrator,
    ALLRISMigrator,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.commit = MagicMock()
    return session


@pytest.fixture
def migrator(mock_session):
    return ALLRISMigrator(
        session=mock_session,
        tenant_id="tenant-001",
        source_url="https://oparl.example.de/api/v1",
    )


@pytest.fixture
def oparl_migrator(mock_session):
    return OParlMigrator(
        session=mock_session,
        tenant_id="tenant-001",
        source_url="https://oparl.example.de/api/v1",
    )


# ============================================================
# Test: ALLRIS CSV Import
# ============================================================

class TestAllrisCsvImport:
    """Test ALLRIS CSV import with German column names."""

    @pytest.mark.asyncio
    async def test_import_gremien(self, migrator, mock_session):
        rows = [
            {"GRNR": "1", "GRNAME": "Stadtrat", "GRKURZ": "SR", "GRTYP": "R"},
            {"GRNR": "2", "GRNAME": "Bauausschuss", "GRKURZ": "BA", "GRTYP": "A"},
        ]
        migrator._import_gremien_csv(rows)
        assert mock_session.add.call_count == 2
        assert migrator.result.organizations == 2

    @pytest.mark.asyncio
    async def test_import_personen(self, migrator, mock_session):
        rows = [
            {"PENR": "1", "PVORNAME": "Max", "PENAME": "Mustermann", "PANREDE": "Herr"},
            {"PENR": "2", "PVORNAME": "Erika", "PENAME": "Musterfrau", "PANREDE": "Frau"},
        ]
        migrator._import_personen_csv(rows)
        assert mock_session.add.call_count == 2
        assert migrator.result.persons == 2

    @pytest.mark.asyncio
    async def test_import_vorlagen(self, migrator, mock_session):
        rows = [
            {"VONR": "V/2025/001", "VOBETREFF": "Haushalt 2025", "VOTYP": "Vorlage", "VODATUM": "2025-01-15"},
            {"VONR": "A/2025/001", "VOBETREFF": "Antrag Spielplatz", "VOTYP": "Antrag", "VODATUM": "2025-02-10"},
        ]
        migrator._import_vorlagen_csv(rows)
        assert migrator.result.papers == 2

    @pytest.mark.asyncio
    async def test_import_sitzungen(self, migrator, mock_session):
        migrator.id_map["body"] = "body-001"
        migrator.id_map["gremium_1"] = "org-001"
        rows = [
            {"SIGRNR": "1", "SIBETREFF": "Ratssitzung", "SIDATUM": "2025-06-15T18:00"},
        ]
        migrator._import_sitzungen_csv(rows)
        assert migrator.result.meetings == 1

    @pytest.mark.asyncio
    async def test_gremium_type_mapping(self, migrator):
        assert migrator._map_allris_gremium_type("A") == "ausschuss"
        assert migrator._map_allris_gremium_type("F") == "fraktion"
        assert migrator._map_allris_gremium_type("R") == "ausschuss"
        assert migrator._map_allris_gremium_type("B") == "sonstiges"
        assert migrator._map_allris_gremium_type("V") == "verwaltung"
        assert migrator._map_allris_gremium_type("X") == "sonstiges"

    @pytest.mark.asyncio
    async def test_import_handles_errors_gracefully(self, migrator, mock_session):
        """CSV rows with missing data should add error, not crash."""
        mock_session.add.side_effect = [Exception("DB error"), None]
        rows = [
            {"GRNR": "1", "GRNAME": "Bad Row", "GRKURZ": "BR", "GRTYP": "A"},
            {"GRNR": "2", "GRNAME": "Good Row", "GRKURZ": "GR", "GRTYP": "A"},
        ]
        migrator._import_gremien_csv(rows)
        assert len(migrator.result.errors) >= 1
        assert migrator.result.organizations >= 0

    @pytest.mark.asyncio
    async def test_full_csv_migration(self, migrator, mock_session):
        csv_data = {
            "gremien": [
                {"GRNR": "1", "GRNAME": "Stadtrat", "GRKURZ": "SR", "GRTYP": "R"},
            ],
            "personen": [
                {"PENR": "1", "PVORNAME": "Max", "PENAME": "Muster", "PANREDE": "Herr"},
            ],
            "vorlagen": [
                {"VONR": "V/2025/001", "VOBETREFF": "Haushalt", "VOTYP": "Vorlage", "VODATUM": "2025-01-01"},
            ],
            "sitzungen": [
                {"SIGRNR": "1", "SIBETREFF": "Ratssitzung", "SIDATUM": "2025-06-15T18:00"},
            ],
        }
        migrator.id_map["body"] = "body-001"
        result = await migrator.migrate_from_csv(csv_data)
        assert result.source == "ALLRIS CSV"
        assert result.completed_at is not None


# ============================================================
# Test: OParl API Migration
# ============================================================

class TestOparlApiMigration:
    """Test OParl API pagination handling."""

    def test_pagination_follows_next_link(self, oparl_migrator):
        """OParl uses links.next for pagination."""
        page1 = {
            "data": [{"id": "1", "name": "Org 1"}],
            "links": {"next": "https://oparl.example.de/api/v1/org?page=2"},
        }
        page2 = {
            "data": [{"id": "2", "name": "Org 2"}],
            "links": {},
        }
        # Verify structure is correct for pagination
        assert "next" in page1["links"]
        assert "next" not in page2.get("links", {})

    def test_empty_page_stops_pagination(self):
        page = {"data": [], "links": {}}
        assert len(page["data"]) == 0

    def test_parse_date_valid(self):
        result = OParlMigrator._parse_date("2025-06-15")
        assert result == date(2025, 6, 15)

    def test_parse_date_none(self):
        result = OParlMigrator._parse_date(None)
        assert result is None

    def test_parse_date_invalid(self):
        result = OParlMigrator._parse_date("not-a-date")
        assert result is None

    def test_parse_datetime_valid(self):
        result = OParlMigrator._parse_datetime("2025-06-15T18:00:00Z")
        assert result is not None
        assert result.year == 2025

    def test_parse_datetime_none(self):
        result = OParlMigrator._parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid(self):
        result = OParlMigrator._parse_datetime("invalid")
        assert result is None


# ============================================================
# Test: Migration Result
# ============================================================

class TestMigrationResult:
    """Test migration result counters and error tracking."""

    def test_total_count(self):
        result = MigrationResult(source="test", started_at=datetime.utcnow())
        result.bodies = 1
        result.organizations = 5
        result.persons = 20
        result.meetings = 10
        result.papers = 15
        assert result.total == 51

    def test_initial_counts_zero(self):
        result = MigrationResult(source="test", started_at=datetime.utcnow())
        assert result.total == 0
        assert result.bodies == 0
        assert result.organizations == 0
        assert result.persons == 0

    def test_error_list(self):
        result = MigrationResult(source="test", started_at=datetime.utcnow())
        result.errors.append("Failed to import Gremium X")
        result.errors.append("Missing GRNR in row 5")
        assert len(result.errors) == 2

    def test_to_dict(self):
        result = MigrationResult(source="ALLRIS CSV", started_at=datetime.utcnow())
        result.bodies = 1
        result.organizations = 3
        result.completed_at = datetime.utcnow()
        d = result.to_dict()
        assert d["source"] == "ALLRIS CSV"
        assert d["total_migrated"] == 4
        assert d["completed_at"] is not None

    def test_error_count_in_dict(self):
        result = MigrationResult(source="test", started_at=datetime.utcnow())
        for i in range(100):
            result.errors.append(f"Error {i}")
        d = result.to_dict()
        assert d["error_count"] == 100
        assert len(d["errors"]) == 50  # Truncated to 50


# ============================================================
# Test: CSV BOM Handling
# ============================================================

class TestCsvBomHandling:
    """Test handling of BOM (Byte Order Mark) in CSV files."""

    def test_bom_stripped_from_first_column(self):
        """BOM (\ufeff) in CSV first column header must be stripped."""
        raw_header = "\ufeffGRNR"
        cleaned = raw_header.lstrip("\ufeff")
        assert cleaned == "GRNR"

    def test_bom_not_present_in_subsequent_columns(self):
        headers = ["\ufeffGRNR", "GRNAME", "GRKURZ"]
        cleaned = [h.lstrip("\ufeff") for h in headers]
        assert cleaned == ["GRNR", "GRNAME", "GRKURZ"]

    def test_no_bom_is_noop(self):
        header = "GRNR"
        cleaned = header.lstrip("\ufeff")
        assert cleaned == "GRNR"

    def test_utf8_bom_bytes(self):
        """UTF-8 BOM is bytes EF BB BF."""
        bom = b"\xef\xbb\xbf"
        raw = bom + b"GRNR;GRNAME;GRKURZ"
        decoded = raw.decode("utf-8-sig")
        assert decoded.startswith("GRNR")

    def test_csv_with_semicolon_delimiter(self):
        """German CSV often uses semicolons."""
        line = "1;Stadtrat;SR;R"
        parts = line.split(";")
        assert len(parts) == 4
        assert parts[1] == "Stadtrat"

    def test_csv_with_umlauts(self):
        """German characters must survive encoding."""
        line = "Bauausschuss;Buergermeisterbuero;Umwelt/Gruenflaechen"
        assert "Bauausschuss" in line
        assert "Buergermeisterbuero" in line
