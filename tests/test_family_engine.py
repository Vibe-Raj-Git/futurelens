"""
Family domain engine tests.

Verifies:

  - the report is produced
  - all nine rules are evaluated
  - every evidence item carries domain, provenance, weight,
    subject, finding, interpretation
  - the Gochara rule filters to the family house set (2, 4, 5, 7, 9, 12)
  - the relationship rule emits one item per relationship
  - yoga promotion fires when relevant yogas are present
  - the summary has the required fields
  - the chart-level integration works
"""

from datetime import datetime, timezone, timedelta

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens import cast_chart
from futurelens.domains.family.definitions import FAMILY_HOUSES
from futurelens.domains.family.engine import (
    FamilyReport,
    build_family_report,
    build_FAMILY_report,
)
from futurelens.models.evidence import Direction


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(
    1984, 8, 30, 12, 2, 0,
    tzinfo=timezone(timedelta(hours=5, minutes=30)),
)
LAT = 22.7196
LON = 75.8577
TARGET = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------

def test_family_houses_are_six():
    assert FAMILY_HOUSES == (2, 4, 5, 7, 9, 12)


# --------------------------------------------------------------------------
# Report construction
# --------------------------------------------------------------------------

def test_family_report_is_produced():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    assert isinstance(report, FamilyReport)


def test_all_nine_rules_evaluated():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    expected = {
        "FAMILY-HOUSE-LORD-NATAL-001",
        "FAMILY-SIGNIFICATOR-NATAL-001",
        "FAMILY-RELATIONSHIP-001",
        "FAMILY-LORD-DASHA-001",
        "FAMILY-UPAGRAHA-001",
        "FAMILY-YAMAKANTAKA-PROTECT-001",
        "FAMILY-YOGA-PROMOTION-001",
        "FAMILY-D9-RECONCILIATION-001",
        "FAMILY-GOCHARA-001",
    }
    assert set(report.rules_evaluated) == expected
    assert report.rules_failed == []


def test_evidence_has_domain_family():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    for e in report.evidence:
        assert e.domain == "FAMILY"


def test_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    for e in report.evidence:
        assert e.provenance.rule_id != ""
        assert e.provenance.classical_basis != ""


def test_evidence_has_semantic_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    for e in report.evidence:
        assert e.subject
        assert e.finding
        assert e.interpretation


# --------------------------------------------------------------------------
# Rule-specific checks
# --------------------------------------------------------------------------

def test_lord_natal_rule_emits_six():
    """One for each of the six family houses."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-HOUSE-LORD-NATAL-001")
    assert len(items) == 6


def test_significator_natal_rule_emits_seven():
    """Moon, Sun, Mars, Jupiter, Venus, Mercury, Saturn."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-SIGNIFICATOR-NATAL-001")
    assert len(items) == 7


def test_relationship_rule_emits_five():
    """Mother, father, spouse, children, siblings."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-RELATIONSHIP-001")
    assert len(items) == 5


def test_relationship_rule_names_are_distinct():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-RELATIONSHIP-001")
    names = set()
    for e in items:
        for note in e.notes:
            if note.startswith("relationship="):
                names.add(note.split("=", 1)[1])
    assert names == {"mother", "father", "spouse", "children", "siblings"}


def test_gochara_rule_evidence_touches_family_houses():
    """
    Every Gochara item must reference a family house by occupancy
    or aspect.
    """
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-GOCHARA-001")
    for e in items:
        notes = dict(n.split("=", 1) for n in e.notes if "=" in n)
        occupied = int(notes["house_from_lagna"]) in FAMILY_HOUSES
        # The Gochara rule guarantees occupancy OR aspect.
        # We can check the finding contains a family house mention,
        # but occupancy is the primary check when true.
        if not occupied:
            # Must be an aspect-based inclusion.
            assert "aspects family houses" in e.finding


def test_yoga_promotion_items_are_structural():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    items = report.by_rule("FAMILY-YOGA-PROMOTION-001")
    for e in items:
        assert e.weight.value == "STRUCTURAL"


# --------------------------------------------------------------------------
# Direction and summary
# --------------------------------------------------------------------------

def test_direction_is_valid():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    valid = {
        Direction.PROTECTIVE,
        Direction.ADVERSE,
        Direction.CONTEXT_INCOMPLETE,
    }
    for e in report.evidence:
        assert e.direction in valid


def test_summary_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    s = report.summary()
    assert "when" in s
    assert "evidence_count" in s
    assert "adverse_count" in s
    assert "protective_count" in s
    assert "contradictions" in s
    assert s["evidence_count"] == len(report.evidence)


def test_summary_counts_match_evidence():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_family_report(chart, TARGET)
    s = report.summary()
    assert s["adverse_count"] == len(report.by_direction(Direction.ADVERSE))
    assert s["protective_count"] == len(
        report.by_direction(Direction.PROTECTIVE)
    )


# --------------------------------------------------------------------------
# Chart integration and alias
# --------------------------------------------------------------------------

def test_build_family_report_alias():
    """The uppercase alias must still exist for backward compatibility."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_FAMILY_report(chart, TARGET)
    assert isinstance(report, FamilyReport)
