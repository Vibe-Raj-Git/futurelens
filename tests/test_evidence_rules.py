"""
Individual rule tests.

These tests use a real chart cast via cast_chart() so that the rule
evaluation is exercised end-to-end against genuine ephemeris data.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.evidence.rules.base import EvidenceContext
from futurelens.evidence.rules.natal_placement import NatalPlacementRule
from futurelens.evidence.rules.sade_sati import SadeSatiRule
from futurelens.evidence.rules.upagraha_dasha import UpagrahaDashaRule
from futurelens.models.evidence import EvidenceType


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


# --- Upagraha dasha rule --------------------------------------------------

def test_upagraha_dasha_rule_applies():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    rule = UpagrahaDashaRule()
    assert rule.applies_to(ctx) is True


def test_upagraha_dasha_rule_emits_list():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = UpagrahaDashaRule().emit(ctx)
    assert isinstance(items, list)


def test_upagraha_dasha_rule_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = UpagrahaDashaRule().emit(ctx)
    for e in items:
        assert e.provenance.rule_id == "UPG-DASHA-001"
        assert e.provenance.tradition == "PHALADEEPIKA"
        assert e.evidence_type == EvidenceType.UPAGRAHA_DASHA_ACTIVATION


# --- Sade Sati rule -------------------------------------------------------

def test_sade_sati_rule_applies():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    assert SadeSatiRule().applies_to(ctx) is True


def test_sade_sati_emits_at_most_one():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = SadeSatiRule().emit(ctx)
    assert len(items) <= 1


def test_sade_sati_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = SadeSatiRule().emit(ctx)
    for e in items:
        assert e.provenance.rule_id == "SAT-SADE-SATI-001"
        assert e.provenance.tradition == "GOCHARA"


# --- Natal placement rule -------------------------------------------------

def test_natal_placement_emits_all_grahas():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = NatalPlacementRule().emit(ctx)
    # One per graha with a house assigned.
    expected = sum(
        1 for pos in chart.grahas.values() if pos.house is not None
    )
    assert len(items) == expected


def test_natal_placement_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    items = NatalPlacementRule().emit(ctx)
    for e in items:
        assert e.provenance.rule_id == "NATAL-PLACEMENT-001"
        assert e.evidence_type == EvidenceType.UPAGRAHA_NATAL_PLACEMENT
