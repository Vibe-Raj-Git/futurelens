"""
Prompt builder and contract tests.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.llm.contract import (
    FORBIDDEN_KEYS,
    assert_payload_safe,
)
from futurelens.llm.prompt import SYSTEM_PROMPT, build_request


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_system_prompt_mentions_no_generation():
    assert "do NOT generate" in SYSTEM_PROMPT.lower() or \
           "do not generate" in SYSTEM_PROMPT.lower()


def test_assert_payload_safe_accepts_safe_payload():
    assert_payload_safe({"domain": "WEALTH", "notes": ["graha=SUN"]})


def test_assert_payload_safe_rejects_longitude():
    with pytest.raises(ValueError):
        assert_payload_safe({"longitude": 123.4})


def test_assert_payload_safe_rejects_nested_longitude():
    with pytest.raises(ValueError):
        assert_payload_safe({"chart": {"graha": {"longitude": 1.0}}})


def test_forbidden_keys_includes_longitude():
    assert "longitude" in FORBIDDEN_KEYS
    assert "sidereal_longitude" in FORBIDDEN_KEYS


def test_build_request_from_wealth_report():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)
    assert request.domain == "WEALTH"
    assert request.when_iso == TARGET.isoformat()
    assert "evidence" in request.payload
    assert len(request.payload["evidence"]) > 0


def test_build_request_payload_has_no_forbidden_keys():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)
    # Should not raise.
    assert_payload_safe(request.payload)


def test_build_request_with_question():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report, question="How is my savings?")
    assert request.payload["question"] == "How is my savings?"
    assert "How is my savings?" in request.user_prompt
