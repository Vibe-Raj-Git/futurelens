"""
LLM backend protocol.

A backend takes an LLMRequest and returns an LLMResponse.

Backends must not access the chart directly. They receive only the
payload built by the prompt module, which is already sanitized.
"""

from __future__ import annotations

from typing import Protocol

from futurelens.llm.contract import LLMRequest, LLMResponse


class LLMBackend(Protocol):
    """Every LLM backend implements this."""

    name: str

    def generate(self, request: LLMRequest) -> LLMResponse:
        ...
