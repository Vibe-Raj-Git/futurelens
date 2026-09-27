"""Career domain engine tests."""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.domains.career.definitions import (
    CAREER_HOUSES,
    CAREER_RELEVANT_YOGAS,
    CAREER_SIGNIFICATORS,
    is_career_house,
    is_dusthana,
    is_kendra,
    is_trikona,
)
from futurelens.domains.career.engine import (
    CareerReport,
    build_career_report,
)
from futurelens.models.evidence import Direction


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_career_houses():
    assert CAREER_HOUSES == (10, 6, 2, 11)


def test_career_predicates():
    assert is_career_house(10)
    assert is_career_house(6)
    assert not is_career_house(1)
    assert is_dusthana(6)
    assert is_kendra(10)
    assert is_trikona(9)


def test_career_significators():
    assert set(CAREER_SIGNIFICATORS) == {
        "SUN", "SATURN", "MERCURY", "JUPITER", "MARS"
    }


def test_career_yogas_defined():
    assert "RAJA_YOGA" in CAREER_RELEVANT_YOGAS
    assert "PANCHA_MAHAPURUSHA" in CAREER_RELEVANT_YOGAS


def test_career_report_is_produced():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    assert isinstance(report, CareerReport)


def test_all_eight_rules_evaluated():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    expected = {
        "CAREER-HOUSE-LORD-NATAL-001",
        "CAREER-SIGNIFICATOR-NATAL-001",
        "CAREER-LORD-DASHA-001",
        "CAREER-UPAGRAHA-001",
        "CAREER-AMALA-YOGA-001",
        "CAREER-YOGA-PROMOTION-001",
        "CAREER-D9-RECONCILIATION-001",
        "CAREER-GOCHARA-001",
    }
    assert set(report.rules_evaluated) == expected
    assert report.rules_failed == []


def test_evidence_has_domain_career():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    for e in report.evidence:
        assert e.domain == "CAREER"


def test_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    for e in report.evidence:
        assert e.provenance.rule_id != ""
        assert e.provenance.classical_basis != ""


def test_career_lord_natal_emits_four():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    items = report.by_rule("CAREER-HOUSE-LORD-NATAL-001")
    assert len(items) == 4


def test_career_significator_natal_emits_five():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    items = report.by_rule("CAREER-SIGNIFICATOR-NATAL-001")
    assert len(items) == 5


def test_yoga_promotion_only_emits_for_present_yogas():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    items = report.by_rule("CAREER-YOGA-PROMOTION-001")
    # Only present career-relevant yogas should produce evidence.
    for e in items:
        notes = dict(n.split("=", 1) for n in e.notes if "=" in n)
        assert notes["yoga_id"] in CAREER_RELEVANT_YOGAS


def test_amala_rule_only_emits_when_benefic_in_10th():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    items = report.by_rule("CAREER-AMALA-YOGA-001")
    for e in items:
        notes = dict(n.split("=", 1) for n in e.notes if "=" in n)
        assert notes.get("yoga") == "AMALA"


def test_summary_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_career_report(chart, TARGET)
    s = report.summary()
    for key in ("when", "evidence_count", "adverse_count",
                "protective_count", "contradictions"):
        assert key in s
    assert s["evidence_count"] == len(report.evidence)


def test_chart_career_method():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.career(TARGET)
    assert isinstance(report, CareerReport)
    assert len(report.evidence) > 0


def test_chart_explain_career_method():
    chart = cast_chart(BIRTH, LAT, LON)
    explanation = chart.explain_career(TARGET)
    assert explanation.evidence_count > 0
    assert len(explanation.text) > 0
