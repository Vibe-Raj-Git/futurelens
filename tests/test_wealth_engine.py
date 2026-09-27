"""
Wealth domain engine tests.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.domains.wealth.definitions import (
    WEALTH_HOUSES,
    is_dusthana,
    is_kendra,
    is_trikona,
    is_wealth_house,
)
from futurelens.domains.wealth.engine import (
    WealthReport,
    build_wealth_report,
)
from futurelens.models.evidence import Direction


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_wealth_houses():
    assert WEALTH_HOUSES == (2, 5, 9, 11)


def test_wealth_house_predicate():
    assert is_wealth_house(2)
    assert is_wealth_house(11)
    assert not is_wealth_house(1)


def test_dusthana_predicate():
    assert is_dusthana(6)
    assert is_dusthana(8)
    assert is_dusthana(12)


def test_kendra_predicate():
    assert is_kendra(1)
    assert is_kendra(10)


def test_trikona_predicate():
    assert is_trikona(1)
    assert is_trikona(5)
    assert is_trikona(9)


def test_wealth_report_is_produced():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    assert isinstance(report, WealthReport)


def test_all_six_rules_evaluated():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    expected = {
        "WEALTH-HOUSE-LORD-NATAL-001",
        "WEALTH-SIGNIFICATOR-NATAL-001",
        "WEALTH-LORD-DASHA-001",
        "WEALTH-SIGNIFICATOR-TRANSIT-001",
        "WEALTH-UPAGRAHA-001",
        "WEALTH-YAMAKANTAKA-PROTECT-001",
    }
    assert set(report.rules_evaluated) == expected
    assert report.rules_failed == []


def test_evidence_has_domain_wealth():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    for e in report.evidence:
        assert e.domain == "WEALTH"


def test_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    for e in report.evidence:
        assert e.provenance.rule_id != ""
        assert e.provenance.tradition != ""
        assert e.provenance.classical_basis != ""


def test_wealth_lord_natal_rule_emits_four():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-HOUSE-LORD-NATAL-001")
    assert len(items) == 4


def test_wealth_significator_natal_rule_emits_five():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-SIGNIFICATOR-NATAL-001")
    assert len(items) == 5


def test_wealth_upagraha_rule_only_emits_for_wealth_houses():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-UPAGRAHA-001")
    for e in items:
        notes = dict(n.split("=", 1) for n in e.notes if "=" in n)
        assert int(notes["house"]) in WEALTH_HOUSES


def test_summary_has_required_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    summary = report.summary()
    for key in ("when", "evidence_count", "adverse_count",
                "protective_count", "contradictions"):
        assert key in summary
    assert summary["evidence_count"] == len(report.evidence)


def test_summary_counts_match_evidence():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    summary = report.summary()
    assert summary["adverse_count"] == len(report.by_direction(Direction.ADVERSE))
    assert summary["protective_count"] == len(report.by_direction(Direction.PROTECTIVE))


def test_chart_wealth_method():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    assert isinstance(report, WealthReport)
    assert len(report.evidence) > 0


def test_wealth_contradictions_are_bounded():
    """
    With the subject-aware detector, contradictions should be far
    fewer than the total number of adverse x protective pairs.
    """
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    adverse = len(report.by_direction(Direction.ADVERSE))
    protective = len(report.by_direction(Direction.PROTECTIVE))
    max_pairs = adverse * protective
    if max_pairs > 0:
        assert len(report.contradictions) < max_pairs
