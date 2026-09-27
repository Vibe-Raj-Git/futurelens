"""Sanitizer tests."""

from futurelens.llm.sanitize import (
    UNVERIFIED_MARKER,
    sanitize_citations,
)


def test_all_valid_citations_kept():
    text = "Some claim [A-001] and another [B-002]."
    result = sanitize_citations(text, {"A-001", "B-002"})
    assert result.text == text
    assert set(result.valid_cited) == {"A-001", "B-002"}
    assert result.redacted_cited == ()


def test_invalid_citations_redacted():
    text = "Real [A-001] and fake [FAKE-999]."
    result = sanitize_citations(text, {"A-001"})
    assert "[A-001]" in result.text
    assert UNVERIFIED_MARKER in result.text
    assert "[FAKE-999]" not in result.text
    assert "FAKE-999" in result.redacted_cited


def test_multiple_invalid_redacted():
    text = "[A-001] [FAKE-1] [FAKE-2] [B-002]"
    result = sanitize_citations(text, {"A-001", "B-002"})
    assert result.text.count(UNVERIFIED_MARKER) == 2
    assert set(result.redacted_cited) == {"FAKE-1", "FAKE-2"}
    assert set(result.valid_cited) == {"A-001", "B-002"}


def test_repeated_invalid_redacted_each_time():
    text = "[FAKE-1] appears twice: [FAKE-1]."
    result = sanitize_citations(text, set())
    assert result.text.count(UNVERIFIED_MARKER) == 2
    assert result.redacted_cited == ("FAKE-1",)


def test_no_citations_returns_unchanged():
    text = "No citations here."
    result = sanitize_citations(text, {"A-001"})
    assert result.text == text
    assert result.valid_cited == ()
    assert result.redacted_cited == ()


def test_lowercase_not_treated_as_citation():
    text = "[lowercase-not-a-citation]"
    result = sanitize_citations(text, set())
    assert result.text == text
    assert result.redacted_cited == ()


def test_empty_valid_set_redacts_all():
    text = "[A-001] [B-002]"
    result = sanitize_citations(text, set())
    assert result.text.count(UNVERIFIED_MARKER) == 2
    assert set(result.redacted_cited) == {"A-001", "B-002"}
