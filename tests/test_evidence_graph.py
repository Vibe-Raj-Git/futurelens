"""
Evidence graph aggregator tests.

Verifies:

  - the graph evaluates all registered rules
  - evidence items carry valid provenance
  - contradiction detection works on same-subject pairs only
  - the Chart.evidence() method works
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.evidence.graph import (
    DEFAULT_RULES,
    Contradiction,
    EvidenceGraph,
    _detect_contradictions,
    build_evidence_graph,
)
from futurelens.evidence.rules.base import EvidenceContext
from futurelens.models.evidence import Direction, Evidence, EvidenceType
from futurelens.models.provenance import Provenance


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def _make(rule_id, direction, notes, domain="WEALTH"):
    return Evidence(
        evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
        direction=direction,
        domain=domain,
        upagraha=None,
        target_evidence_id=None,
        classical_strength_ratio=1.0,
        provenance=Provenance(
            rule_id=rule_id, rule_version="0.1", tradition="T",
            classical_basis="B", calculation_method="M",
            calculation_convention="C",
        ),
        notes=notes,
    )


# --- Basic construction ---------------------------------------------------

def test_build_evidence_graph_returns_graph():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    graph = build_evidence_graph(ctx)
    assert isinstance(graph, EvidenceGraph)


def test_graph_evaluates_default_rules():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    graph = build_evidence_graph(ctx)
    assert len(graph.rules_evaluated) == len(DEFAULT_RULES)
    assert graph.rules_failed == []


def test_graph_has_evidence():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    graph = build_evidence_graph(ctx)
    assert len(graph.evidence) > 0


def test_every_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    graph = build_evidence_graph(ctx)
    for e in graph.evidence:
        assert e.provenance.rule_id != ""
        assert e.provenance.tradition != ""
        assert e.provenance.classical_basis != ""


def test_by_rule_filter():
    chart = cast_chart(BIRTH, LAT, LON)
    ctx = EvidenceContext(chart=chart, when=TARGET)
    graph = build_evidence_graph(ctx)
    natal = graph.by_rule("NATAL-PLACEMENT-001")
    assert len(natal) == 9


# --- Contradiction detection ---------------------------------------------

def test_no_contradictions_when_all_same_direction():
    items = [
        _make("R1", Direction.ADVERSE, ("graha=SUN", "house=2")),
        _make("R2", Direction.ADVERSE, ("graha=SUN", "house=2")),
    ]
    assert _detect_contradictions(items) == []


def test_no_contradictions_across_different_subjects():
    """Two adverse-vs-protective pairs on different subjects are not contradictions."""
    items = [
        _make("R1", Direction.ADVERSE, ("graha=MERCURY", "house=12")),
        _make("R2", Direction.PROTECTIVE, ("graha=MARS", "house=9")),
    ]
    assert _detect_contradictions(items) == []


def test_contradiction_on_same_graha_house():
    items = [
        _make("R1", Direction.ADVERSE, ("graha=SUN", "house=2")),
        _make("R2", Direction.PROTECTIVE, ("graha=SUN", "house=2")),
    ]
    c = _detect_contradictions(items)
    assert len(c) == 1
    assert isinstance(c[0], Contradiction)
    assert c[0].subject == "natal:graha:SUN@house:2"


def test_contradiction_on_same_upagraha():
    items = [
        _make("R1", Direction.ADVERSE, ("upagraha=GULIKA", "house=2")),
        _make("R2", Direction.PROTECTIVE, ("upagraha=GULIKA", "house=2")),
    ]
    c = _detect_contradictions(items)
    assert len(c) == 1
    assert c[0].subject == "natal:upagraha:GULIKA"


def test_standalone_items_not_eligible_for_contradiction():
    """Evidence without a subject key is not eligible."""
    items = [
        _make("R1", Direction.ADVERSE, ("note=something",)),
        _make("R2", Direction.PROTECTIVE, ("note=else",)),
    ]
    assert _detect_contradictions(items) == []


# --- Chart integration ----------------------------------------------------

def test_chart_evidence_method():
    chart = cast_chart(BIRTH, LAT, LON)
    graph = chart.evidence(TARGET)
    assert isinstance(graph, EvidenceGraph)
    assert len(graph.evidence) > 0


def test_chart_evidence_method_with_domain_filter():
    chart = cast_chart(BIRTH, LAT, LON)
    graph = chart.evidence(TARGET, domain="WEALTH")
    assert isinstance(graph, EvidenceGraph)

def test_no_contradiction_across_layers():
    """
    A natal item and a transit item about the same graha are never
    contradictory. They describe different planes of reality - the
    chart's promise vs. the current sky. The layer prefix in the
    subject key prevents them from being bucketed together.
    """
    items = [
        _make("WEALTH-D9-RECONCILIATION-001", Direction.PROTECTIVE,
              ("graha=JUPITER",)),
        _make("WEALTH-GOCHARA-001", Direction.ADVERSE,
              ("graha=JUPITER", "transit_graha=JUPITER")),
    ]
    assert _detect_contradictions(items) == []

def test_contradiction_within_natal_layer():
    """
    Two natal items about the same graha and house still pair as
    contradictory when their directions oppose.
    """
    items = [
        _make("WEALTH-HOUSE-LORD-NATAL-001", Direction.PROTECTIVE,
              ("graha=JUPITER", "house=2")),
        _make("WEALTH-SIGNIFICATOR-NATAL-001", Direction.ADVERSE,
              ("graha=JUPITER", "house=2")),
    ]
    c = _detect_contradictions(items)
    assert len(c) == 1
    assert c[0].subject == "natal:graha:JUPITER@house:2"