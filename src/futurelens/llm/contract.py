"""
The LLM contract.

This module enforces the boundary between what the engine computes
and what the LLM may say. Every payload sent to a backend must
conform to a strict schema, and every backend response is parsed
and validated against the evidence it received.

Design principles:
  - The LLM does not receive raw longitudes or ephemeris data.
  - The LLM receives only evidence items with a rule_id.
  - The LLM must not invent new astrology. It explains evidence.
  - Every claim in the response must cite at least one rule_id.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Keys that must NEVER appear in an LLM payload.
FORBIDDEN_KEYS: frozenset[str] = frozenset({
    "longitude",
    "tropical_longitude",
    "sidereal_longitude",
    "obliquity",
    "lst_degrees",
    "sunrise",
    "sunset",
    "birth_datetime",
})


def assert_payload_safe(payload: dict[str, Any]) -> None:
    """
    Walk the payload and raise if any forbidden key is present.
    This is a guardrail, not a security boundary.
    """
    def _walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in FORBIDDEN_KEYS:
                    raise ValueError(
                        f"Forbidden key '{k}' found at {path or '<root>'} "
                        f"in LLM payload."
                    )
                _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                _walk(item, f"{path}[{i}]")

    _walk(payload, "")


@dataclass(frozen=True)
class LLMRequest:
    """A structured request to an LLM backend."""

    system_prompt: str
    user_prompt: str
    payload: dict[str, Any]
    domain: str
    when_iso: str


@dataclass(frozen=True)
class LLMResponse:
    """A parsed response from an LLM backend."""

    text: str
    rule_ids_cited: tuple[str, ...]
    backend: str
    raw: dict[str, Any] | None = None
