"""
Explainer tests using the deterministic template backend.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.llm.backends.template import TemplateBackend, _describe
from futurelens.llm.explainer import Explanation, explain


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_explain_returns_explanation():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    result = explain(report)
    assert isinstance(result, Explanation)


def test_explanation_has_text():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    result = explain(report)
    assert len(result.text) > 0


def test_explanation_cites_rule_ids():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    result = explain(report)
    evidence_rules = {e.provenance.rule_id for e in report.evidence}
    for rid in result.rule_ids_cited:
        assert rid in evidence_rules


def test_template_backend_name():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    result = explain(report, backend=TemplateBackend())
    assert result.backend == "template"


def test_chart_explain_wealth_method():
    chart = cast_chart(BIRTH, LAT, LON)
    result = chart.explain_wealth(TARGET)
    assert isinstance(result, Explanation)


def test_explanation_cites_at_least_one_rule():
    """
    The template backend always cites rule IDs in square brackets.
    This test verifies that at least one citation appears in the
    explanation, which is the contract the LLM layer guarantees.
    """
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    result = explain(report)
    assert len(result.rule_ids_cited) > 0
    for rid in result.rule_ids_cited:
        assert f"[{rid}]" in result.text


def test_describe_house_lord_with_reason():
    e = {
        "rule_id": "WEALTH-HOUSE-LORD-NATAL-001",
        "direction": "ADVERSE",
        "finding": (
            "MERCURY is in the 12th house, Libra."
        ),
        "interpretation": (
            "The 2nd house relates to accumulated wealth. "
            "The placement is a difficult placement."
        ),
    }
    desc = _describe(e)
    assert "MERCURY" in desc
    assert "12th house" in desc
    assert "difficult placement" in desc
    assert "[WEALTH-HOUSE-LORD-NATAL-001]" in desc


def test_describe_significator_with_combust():
    e = {
        "rule_id": "WEALTH-SIGNIFICATOR-NATAL-001",
        "direction": "ADVERSE",
        "finding": (
            "JUPITER is in the 11th house, Gemini. It is combust, "
            "which weakens its effect."
        ),
        "interpretation": (
            "JUPITER signifies abundance. The placement is weakened "
            "by combustion."
        ),
    }
    desc = _describe(e)
    assert "JUPITER" in desc
    assert "combust" in desc.lower()
    assert "[WEALTH-SIGNIFICATOR-NATAL-001]" in desc


def test_describe_yamakantaka_protect():
    e = {
        "rule_id": "WEALTH-YAMAKANTAKA-PROTECT-001",
        "direction": "PROTECTIVE",
        "finding": (
            "Yamakantaka is in the 2nd house, and its activating "
            "lord MERCURY is currently in dasha."
        ),
        "interpretation": (
            "Yamakantaka provides a protective influence for wealth "
            "during this period."
        ),
    }
    desc = _describe(e)
    assert "Yamakantaka" in desc
    assert "2nd house" in desc
    assert "[WEALTH-YAMAKANTAKA-PROTECT-001]" in desc
