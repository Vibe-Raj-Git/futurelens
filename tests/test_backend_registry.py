"""Backend registry tests."""

import pytest

from futurelens.llm.backends.registry import available, get


def test_available_includes_template():
    assert "template" in available()


def test_available_includes_gemini():
    assert "gemini" in available()


def test_get_template():
    backend = get("template")
    assert backend.name == "template"


def test_get_unknown_raises():
    with pytest.raises(ValueError):
        get("nope")
