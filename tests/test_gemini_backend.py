"""
Gemini backend tests using a mock client.

These tests do NOT call the real Gemini API. They use a fake client
object that mimics the response shape of google.genai.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.llm.backends.gemini import GeminiBackend
from futurelens.llm.prompt import build_request
from futurelens.llm.sanitize import UNVERIFIED_MARKER


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


class _MockResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _MockModels:
    def __init__(self, text: str) -> None:
        self._text = text

    def generate_content(self, model, contents, config):
        return _MockResponse(self._text)


class _MockClient:
    def __init__(self, text: str) -> None:
        self.models = _MockModels(text)


def test_gemini_response_with_valid_citation_kept():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)

    real_rules = [e["rule_id"] for e in request.payload["evidence"]]
    first_rule = real_rules[0]
    mock_text = f"Claim supported by [{first_rule}]."

    backend = GeminiBackend(client=_MockClient(mock_text))
    response = backend.generate(request)

    assert first_rule in response.rule_ids_cited
    assert first_rule in response.text
    assert response.raw["redacted_count"] == 0


def test_gemini_response_with_fake_citation_redacted():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)

    fake_rule = "WEALTH-HOUSE-PLANET-NATAL-002"
    mock_text = f"Claim supported by [{fake_rule}]."

    backend = GeminiBackend(client=_MockClient(mock_text))
    response = backend.generate(request)

    assert fake_rule not in response.rule_ids_cited
    assert fake_rule not in response.text
    assert UNVERIFIED_MARKER in response.text
    assert response.raw["redacted_count"] == 1
    assert fake_rule in response.raw["redacted_cited"]


def test_gemini_response_with_mixed_citations():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)

    real_rules = [e["rule_id"] for e in request.payload["evidence"]]
    mock_text = (
        f"Real [{real_rules[0]}] and fake [FAKE-001] "
        f"and another real [{real_rules[1]}]."
    )

    backend = GeminiBackend(client=_MockClient(mock_text))
    response = backend.generate(request)

    assert real_rules[0] in response.rule_ids_cited
    assert real_rules[1] in response.rule_ids_cited
    assert "FAKE-001" not in response.text
    assert response.raw["redacted_count"] == 1


def test_gemini_response_with_many_fake_citations():
    """
    Simulates the exact failure we saw: an LLM that invents plausible
    looking IDs. All fake IDs should be redacted.
    """
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    request = build_request(report)

    real_rules = [e["rule_id"] for e in request.payload["evidence"]]
    fake_ids = [
        "WEALTH-HOUSE-PLANET-NATAL-002",
        "WEALTH-YOGA-NATAL-004",
        "WEALTH-HOUSE-ASPECT-NATAL-003",
        "WEALTH-EXPENSE-NATAL-009",
    ]
    pieces = [f"Real [{real_rules[0]}]."]
    for f in fake_ids:
        pieces.append(f"Fake [{f}].")
    mock_text = " ".join(pieces)

    backend = GeminiBackend(client=_MockClient(mock_text))
    response = backend.generate(request)

    assert real_rules[0] in response.rule_ids_cited
    assert response.raw["redacted_count"] == len(fake_ids)
    for f in fake_ids:
        assert f not in response.text
    assert response.text.count(UNVERIFIED_MARKER) == len(fake_ids)
