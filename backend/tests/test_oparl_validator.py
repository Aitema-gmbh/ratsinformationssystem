"""
OParl 1.1 Validator

Validates OParl objects against the spec defined in oparl_spec.json.
Used both as a library by test_oparl_conformance.py and as standalone tests.
"""
import json
import re
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Load spec once at module level
_SPEC_PATH = Path(__file__).parent / "oparl_spec.json"
with open(_SPEC_PATH) as f:
    OPARL_SPEC = json.load(f)


# Compiled regex patterns from spec
_RE_URL = re.compile(OPARL_SPEC["url_format"]["regex"])
_RE_DATE = re.compile(OPARL_SPEC["date_formats"]["regex_date"])
_RE_DATETIME = re.compile(OPARL_SPEC["date_formats"]["regex_datetime"])


class OParlValidationError(Exception):
    """Raised when an OParl object fails validation."""

    def __init__(self, object_type: str, field: str, message: str):
        self.object_type = object_type
        self.field = field
        self.message = message
        super().__init__(f"[{object_type}.{field}] {message}")


class OParlValidator:
    """
    Validates OParl 1.1 objects against the specification.

    Usage:
        validator = OParlValidator("Body")
        errors = validator.validate(body_dict)
    """

    OPARL_CONTEXT = "https://schema.oparl.org/1.1/"

    def __init__(self, object_type: str):
        if object_type not in OPARL_SPEC["types"]:
            raise ValueError(f"Unknown OParl type: {object_type}. "
                             f"Valid types: {list(OPARL_SPEC['types'].keys())}")
        self.object_type = object_type
        self.spec = OPARL_SPEC["types"][object_type]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, obj: Dict[str, Any]) -> List[OParlValidationError]:
        """Return all validation errors for the given object dict."""
        errors: List[OParlValidationError] = []
        errors.extend(self._check_required_fields(obj))
        errors.extend(self._check_field_types(obj))
        return errors

    def is_valid(self, obj: Dict[str, Any]) -> bool:
        """Return True if object passes all validations."""
        return len(self.validate(obj)) == 0

    def assert_valid(self, obj: Dict[str, Any]) -> None:
        """Raise OParlValidationError on first violation found."""
        for error in self.validate(obj):
            raise error

    # ------------------------------------------------------------------
    # Required fields
    # ------------------------------------------------------------------

    def _check_required_fields(self, obj: Dict) -> List[OParlValidationError]:
        errors = []
        for field in self.spec["required_fields"]:
            if field not in obj or obj[field] is None or obj[field] == "":
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Required field '{field}' is missing or empty"
                ))
        return errors

    # ------------------------------------------------------------------
    # Field type validation
    # ------------------------------------------------------------------

    def _check_field_types(self, obj: Dict) -> List[OParlValidationError]:
        errors = []
        field_types = self.spec.get("field_types", {})

        for field, expected_type in field_types.items():
            if field not in obj or obj[field] is None:
                continue  # Optional field absent – fine

            value = obj[field]
            type_errors = self._validate_field_value(field, value, expected_type)
            errors.extend(type_errors)

        return errors

    def _validate_field_value(
        self, field: str, value: Any, expected_type: str
    ) -> List[OParlValidationError]:
        errors = []

        if expected_type == "url":
            ok, msg = self.validate_url(value)
            if not ok:
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Invalid URL '{value}': {msg}"
                ))

        elif expected_type == "url_array":
            if not isinstance(value, list):
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Expected list of URLs, got {type(value).__name__}"
                ))
            else:
                for i, url in enumerate(value):
                    ok, msg = self.validate_url(url)
                    if not ok:
                        errors.append(OParlValidationError(
                            self.object_type, f"{field}[{i}]",
                            f"Invalid URL '{url}': {msg}"
                        ))

        elif expected_type == "date":
            ok, msg = self.validate_date(value)
            if not ok:
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Invalid ISO 8601 date '{value}': {msg}"
                ))

        elif expected_type == "datetime":
            ok, msg = self.validate_datetime(value)
            if not ok:
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Invalid ISO 8601 datetime '{value}': {msg}"
                ))

        elif expected_type == "boolean":
            if not isinstance(value, bool):
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Expected boolean, got {type(value).__name__}: {value!r}"
                ))

        elif expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Expected integer, got {type(value).__name__}: {value!r}"
                ))

        elif expected_type == "string":
            if not isinstance(value, str):
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Expected string, got {type(value).__name__}: {value!r}"
                ))

        elif expected_type == "string_array":
            if not isinstance(value, list):
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Expected list of strings, got {type(value).__name__}"
                ))
            else:
                for i, s in enumerate(value):
                    if not isinstance(s, str):
                        errors.append(OParlValidationError(
                            self.object_type, f"{field}[{i}]",
                            f"Expected string, got {type(s).__name__}: {s!r}"
                        ))

        elif expected_type == "geojson":
            ok, msg = self.validate_geojson(value)
            if not ok:
                errors.append(OParlValidationError(
                    self.object_type, field,
                    f"Invalid GeoJSON: {msg}"
                ))

        return errors

    # ------------------------------------------------------------------
    # Static validators (reusable outside this class)
    # ------------------------------------------------------------------

    @staticmethod
    def validate_url(value: Any) -> Tuple[bool, str]:
        """Validate that value is a well-formed http/https URL."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if not _RE_URL.match(value):
            return False, "Must start with http:// or https://"
        return True, ""

    @staticmethod
    def validate_date(value: Any) -> Tuple[bool, str]:
        """Validate ISO 8601 date string (YYYY-MM-DD)."""
        if isinstance(value, (date, datetime)):
            return True, ""
        if not isinstance(value, str):
            return False, f"Expected string or date, got {type(value).__name__}"
        if not _RE_DATE.match(value):
            return False, "Must match YYYY-MM-DD"
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            return False, str(exc)
        return True, ""

    @staticmethod
    def validate_datetime(value: Any) -> Tuple[bool, str]:
        """Validate ISO 8601 datetime string with timezone."""
        if isinstance(value, datetime):
            return True, ""
        if not isinstance(value, str):
            return False, f"Expected string or datetime, got {type(value).__name__}"
        if not _RE_DATETIME.match(value):
            return False, "Must match ISO 8601 datetime with timezone (Z or ±HH:MM)"
        return True, ""

    @staticmethod
    def validate_geojson(value: Any) -> Tuple[bool, str]:
        """Basic GeoJSON structure validation."""
        if not isinstance(value, dict):
            return False, f"Expected dict, got {type(value).__name__}"
        if "type" not in value:
            return False, "GeoJSON must have 'type' field"
        valid_types = {
            "Point", "MultiPoint", "LineString", "MultiLineString",
            "Polygon", "MultiPolygon", "GeometryCollection",
            "Feature", "FeatureCollection",
        }
        if value["type"] not in valid_types:
            return False, f"Invalid GeoJSON type '{value['type']}'"
        return True, ""

    @staticmethod
    def validate_oparl_type_url(value: str, expected_type: str) -> Tuple[bool, str]:
        """Validate that the type field matches the expected OParl type URL."""
        expected = f"https://schema.oparl.org/1.1/{expected_type}"
        if value != expected:
            return False, f"Expected '{expected}', got '{value}'"
        return True, ""

    # ------------------------------------------------------------------
    # Relationship consistency
    # ------------------------------------------------------------------

    def validate_relationships(
        self,
        obj: Dict[str, Any],
        related_objects: Optional[Dict[str, Dict]] = None,
    ) -> List[OParlValidationError]:
        """
        Check that relationship URL fields are consistent.

        If related_objects is provided (mapping URL -> object dict),
        verifies that referenced objects actually exist and have the
        correct type.
        """
        errors = []
        relationships = self.spec.get("relationships", {})

        for field, rel_spec in relationships.items():
            if field not in obj or obj[field] is None:
                continue

            target_type = rel_spec["target"]
            cardinality = rel_spec["cardinality"]
            target_type_url = f"https://schema.oparl.org/1.1/{target_type}"

            if cardinality == "single":
                url = obj[field]
                ok, msg = self.validate_url(url)
                if not ok:
                    errors.append(OParlValidationError(
                        self.object_type, field,
                        f"Relationship URL invalid: {msg}"
                    ))
                elif related_objects and url in related_objects:
                    referenced = related_objects[url]
                    if referenced.get("type") != target_type_url:
                        errors.append(OParlValidationError(
                            self.object_type, field,
                            f"Referenced object has wrong type "
                            f"(expected {target_type_url}, "
                            f"got {referenced.get('type')})"
                        ))

            elif cardinality in ("url_array", "url_list"):
                urls = obj[field] if isinstance(obj[field], list) else []
                for i, url in enumerate(urls):
                    ok, msg = self.validate_url(url)
                    if not ok:
                        errors.append(OParlValidationError(
                            self.object_type, f"{field}[{i}]",
                            f"Relationship URL invalid: {msg}"
                        ))
                    elif related_objects and url in related_objects:
                        referenced = related_objects[url]
                        if referenced.get("type") != target_type_url:
                            errors.append(OParlValidationError(
                                self.object_type, f"{field}[{i}]",
                                f"Referenced object has wrong type "
                                f"(expected {target_type_url}, "
                                f"got {referenced.get('type')})"
                            ))

        return errors


# ==============================================================================
# Pytest tests for the validator itself
# ==============================================================================

import pytest


class TestURLValidation:
    """URL format validation."""

    def test_valid_https_url(self):
        ok, _ = OParlValidator.validate_url("https://example.com/oparl/v1/")
        assert ok

    def test_valid_http_url(self):
        ok, _ = OParlValidator.validate_url("http://localhost:8000/oparl/v1/")
        assert ok

    def test_rejects_empty_string(self):
        ok, msg = OParlValidator.validate_url("")
        assert not ok

    def test_rejects_relative_url(self):
        ok, msg = OParlValidator.validate_url("/oparl/v1/")
        assert not ok

    def test_rejects_ftp_url(self):
        ok, msg = OParlValidator.validate_url("ftp://example.com/file")
        assert not ok

    def test_rejects_none(self):
        ok, msg = OParlValidator.validate_url(None)
        assert not ok

    def test_rejects_integer(self):
        ok, msg = OParlValidator.validate_url(42)
        assert not ok


class TestDateValidation:
    """ISO 8601 date format validation."""

    def test_valid_date_string(self):
        ok, _ = OParlValidator.validate_date("2026-02-20")
        assert ok

    def test_valid_date_object(self):
        ok, _ = OParlValidator.validate_date(date(2026, 2, 20))
        assert ok

    def test_rejects_german_format(self):
        ok, _ = OParlValidator.validate_date("20.02.2026")
        assert not ok

    def test_rejects_us_format(self):
        ok, _ = OParlValidator.validate_date("02/20/2026")
        assert not ok

    def test_rejects_datetime_as_date(self):
        ok, _ = OParlValidator.validate_date("2026-02-20T10:00:00Z")
        assert not ok

    def test_rejects_invalid_month(self):
        ok, _ = OParlValidator.validate_date("2026-13-01")
        assert not ok


class TestDatetimeValidation:
    """ISO 8601 datetime format validation."""

    def test_valid_datetime_utc(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20T10:30:00Z")
        assert ok

    def test_valid_datetime_offset(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20T10:30:00+01:00")
        assert ok

    def test_valid_datetime_negative_offset(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20T10:30:00-05:00")
        assert ok

    def test_valid_datetime_object(self):
        ok, _ = OParlValidator.validate_datetime(datetime(2026, 2, 20, 10, 30))
        assert ok

    def test_rejects_date_only(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20")
        assert not ok

    def test_rejects_no_timezone(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20T10:30:00")
        assert not ok

    def test_valid_datetime_with_microseconds(self):
        ok, _ = OParlValidator.validate_datetime("2026-02-20T10:30:00.123456Z")
        assert ok


class TestGeoJSONValidation:
    """GeoJSON structure validation."""

    def test_valid_point(self):
        ok, _ = OParlValidator.validate_geojson({
            "type": "Point",
            "coordinates": [13.404954, 52.520008]
        })
        assert ok

    def test_valid_feature(self):
        ok, _ = OParlValidator.validate_geojson({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [13.4, 52.5]},
            "properties": {}
        })
        assert ok

    def test_rejects_no_type(self):
        ok, msg = OParlValidator.validate_geojson({"coordinates": [1, 2]})
        assert not ok
        assert "type" in msg

    def test_rejects_invalid_type(self):
        ok, msg = OParlValidator.validate_geojson({"type": "InvalidGeometry"})
        assert not ok

    def test_rejects_non_dict(self):
        ok, msg = OParlValidator.validate_geojson("[1, 2, 3]")
        assert not ok


class TestOParlTypeURL:
    """OParl type URL validation."""

    def test_valid_system_type(self):
        ok, _ = OParlValidator.validate_oparl_type_url(
            "https://schema.oparl.org/1.1/System", "System"
        )
        assert ok

    def test_valid_body_type(self):
        ok, _ = OParlValidator.validate_oparl_type_url(
            "https://schema.oparl.org/1.1/Body", "Body"
        )
        assert ok

    def test_rejects_wrong_version(self):
        ok, _ = OParlValidator.validate_oparl_type_url(
            "https://schema.oparl.org/1.0/Body", "Body"
        )
        assert not ok

    def test_rejects_wrong_type(self):
        ok, _ = OParlValidator.validate_oparl_type_url(
            "https://schema.oparl.org/1.1/Meeting", "Body"
        )
        assert not ok


class TestRequiredFields:
    """Required field checks for each OParl type."""

    def test_system_missing_oparl_version(self):
        validator = OParlValidator("System")
        obj = {
            "id": "https://example.com/oparl/v1/",
            "type": "https://schema.oparl.org/1.1/System",
            "body": "https://example.com/oparl/v1/body",
        }
        errors = validator.validate(obj)
        fields_with_errors = [e.field for e in errors]
        assert "oparl_version" in fields_with_errors

    def test_body_missing_system(self):
        validator = OParlValidator("Body")
        obj = {
            "id": "https://example.com/oparl/v1/body/1",
            "type": "https://schema.oparl.org/1.1/Body",
            "name": "Stadtrat",
            "organization": "https://example.com/oparl/v1/body/1/organization",
            "person": "https://example.com/oparl/v1/body/1/person",
            "meeting": "https://example.com/oparl/v1/body/1/meeting",
            "paper": "https://example.com/oparl/v1/body/1/paper",
            "legislative_term": "https://example.com/oparl/v1/body/1/legislative-term",
        }
        errors = validator.validate(obj)
        fields_with_errors = [e.field for e in errors]
        assert "system" in fields_with_errors

    def test_agenda_item_missing_meeting(self):
        validator = OParlValidator("AgendaItem")
        obj = {
            "id": "https://example.com/oparl/v1/agenda-item/1",
            "type": "https://schema.oparl.org/1.1/AgendaItem",
        }
        errors = validator.validate(obj)
        fields_with_errors = [e.field for e in errors]
        assert "meeting" in fields_with_errors

    def test_file_missing_access_url(self):
        validator = OParlValidator("File")
        obj = {
            "id": "https://example.com/oparl/v1/file/1",
            "type": "https://schema.oparl.org/1.1/File",
        }
        errors = validator.validate(obj)
        fields_with_errors = [e.field for e in errors]
        assert "access_url" in fields_with_errors

    def test_legislative_term_missing_body(self):
        validator = OParlValidator("LegislativeTerm")
        obj = {
            "id": "https://example.com/oparl/v1/legislative-term/1",
            "type": "https://schema.oparl.org/1.1/LegislativeTerm",
        }
        errors = validator.validate(obj)
        fields_with_errors = [e.field for e in errors]
        assert "body" in fields_with_errors

    def test_valid_minimal_organization(self):
        """Organization only requires id and type."""
        validator = OParlValidator("Organization")
        obj = {
            "id": "https://example.com/oparl/v1/organization/1",
            "type": "https://schema.oparl.org/1.1/Organization",
        }
        errors = validator.validate(obj)
        assert errors == []

    def test_valid_minimal_person(self):
        """Person only requires id and type."""
        validator = OParlValidator("Person")
        obj = {
            "id": "https://example.com/oparl/v1/person/1",
            "type": "https://schema.oparl.org/1.1/Person",
        }
        errors = validator.validate(obj)
        assert errors == []


class TestFieldTypeValidation:
    """Field type checks."""

    def test_system_body_must_be_url(self):
        validator = OParlValidator("System")
        obj = {
            "id": "https://example.com/oparl/v1/",
            "type": "https://schema.oparl.org/1.1/System",
            "oparl_version": "https://schema.oparl.org/1.1/",
            "body": "not-a-url",
        }
        errors = validator.validate(obj)
        fields = [e.field for e in errors]
        assert "body" in fields

    def test_organization_start_date_iso(self):
        validator = OParlValidator("Organization")
        obj = {
            "id": "https://example.com/oparl/v1/organization/1",
            "type": "https://schema.oparl.org/1.1/Organization",
            "start_date": "01.01.2020",  # German format - invalid
        }
        errors = validator.validate(obj)
        assert any(e.field == "start_date" for e in errors)

    def test_meeting_created_must_have_timezone(self):
        validator = OParlValidator("Meeting")
        obj = {
            "id": "https://example.com/oparl/v1/meeting/1",
            "type": "https://schema.oparl.org/1.1/Meeting",
            "created": "2026-02-20T10:00:00",  # No timezone - invalid
        }
        errors = validator.validate(obj)
        assert any(e.field == "created" for e in errors)

    def test_membership_voting_right_must_be_bool(self):
        validator = OParlValidator("Membership")
        obj = {
            "id": "https://example.com/oparl/v1/membership/1",
            "type": "https://schema.oparl.org/1.1/Membership",
            "voting_right": "true",  # String, not bool - invalid
        }
        errors = validator.validate(obj)
        assert any(e.field == "voting_right" for e in errors)


class TestRelationshipConsistency:
    """Relationship URL and type consistency checks."""

    def test_body_relationship_to_system(self):
        validator = OParlValidator("Body")
        body = {
            "id": "https://example.com/oparl/v1/body/1",
            "type": "https://schema.oparl.org/1.1/Body",
            "system": "https://example.com/oparl/v1/",
            "name": "Stadtrat",
            "organization": "https://example.com/oparl/v1/body/1/organization",
            "person": "https://example.com/oparl/v1/body/1/person",
            "meeting": "https://example.com/oparl/v1/body/1/meeting",
            "paper": "https://example.com/oparl/v1/body/1/paper",
            "legislative_term": "https://example.com/oparl/v1/body/1/legislative-term",
        }
        related = {
            "https://example.com/oparl/v1/": {
                "id": "https://example.com/oparl/v1/",
                "type": "https://schema.oparl.org/1.1/System",
            }
        }
        errors = validator.validate_relationships(body, related)
        assert errors == []

    def test_detects_wrong_target_type(self):
        validator = OParlValidator("Body")
        body = {
            "id": "https://example.com/oparl/v1/body/1",
            "type": "https://schema.oparl.org/1.1/Body",
            "system": "https://example.com/oparl/v1/body/wrong",
        }
        related = {
            "https://example.com/oparl/v1/body/wrong": {
                "id": "https://example.com/oparl/v1/body/wrong",
                "type": "https://schema.oparl.org/1.1/Body",  # Wrong: should be System
            }
        }
        errors = validator.validate_relationships(body, related)
        assert any(e.field == "system" for e in errors)

    def test_paper_url_array_relationships(self):
        validator = OParlValidator("Paper")
        paper = {
            "id": "https://example.com/oparl/v1/paper/1",
            "type": "https://schema.oparl.org/1.1/Paper",
            "originator_person": [
                "https://example.com/oparl/v1/person/1",
                "not-a-url",  # Invalid URL in array
            ],
        }
        errors = validator.validate_relationships(paper)
        assert any("originator_person" in e.field for e in errors)


class TestSpecCompleteness:
    """Verify the spec file covers all 12 OParl types."""

    EXPECTED_TYPES = [
        "System", "Body", "Organization", "Person", "Membership",
        "Meeting", "AgendaItem", "Paper", "Consultation",
        "File", "Location", "LegislativeTerm",
    ]

    def test_all_12_types_in_spec(self):
        for t in self.EXPECTED_TYPES:
            assert t in OPARL_SPEC["types"], f"Type '{t}' missing from oparl_spec.json"

    def test_all_types_have_required_fields(self):
        for t in self.EXPECTED_TYPES:
            spec = OPARL_SPEC["types"][t]
            assert "required_fields" in spec, f"'{t}' missing required_fields"
            assert isinstance(spec["required_fields"], list)
            assert "id" in spec["required_fields"], f"'{t}' must require 'id'"
            assert "type" in spec["required_fields"], f"'{t}' must require 'type'"

    def test_all_types_have_type_url(self):
        for t in self.EXPECTED_TYPES:
            spec = OPARL_SPEC["types"][t]
            assert "type_url" in spec
            assert spec["type_url"] == f"https://schema.oparl.org/1.1/{t}"

    def test_validator_accepts_all_types(self):
        for t in self.EXPECTED_TYPES:
            validator = OParlValidator(t)
            assert validator.object_type == t

    def test_validator_rejects_unknown_type(self):
        with pytest.raises(ValueError, match="Unknown OParl type"):
            OParlValidator("UnknownType")
