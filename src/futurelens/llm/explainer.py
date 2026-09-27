"""
LLM explainer orchestration.

Takes a domain report, builds a request, calls a backend, validates
the response, and returns a structured result.
"""

from __future__ import annotations

from dataclasses import dataclass

from futurelens.llm.backends.registry import get as get_backend
from futurelens.llm.backends.template import TemplateBackend
from futurelens.llm.contract import LLMResponse
from futurelens.llm.prompt import build_request


DEFAULT_BACKEND = TemplateBackend()


@dataclass(frozen=True)
class Explanation:
    """The result of explaining a domain report."""

    text: str
    backend: str
    rule_ids_cited: tuple[str, ...]
    evidence_count: int
    contradiction_count: int


def _resolve_backend(backend):
    """Accept an instance, a string name, or None (default)."""
    if backend is None:
        return DEFAULT_BACKEND
    if isinstance(backend, str):
        return get_backend(backend)
    return backend


def explain(
    report,
    question: str | None = None,
    backend=None,
) -> Explanation:
    """
    Explain a domain report.

    Parameters
    ----------
    report : WealthReport, CareerReport, or any report with
        when/evidence/contradictions
    question : str, optional
    backend : LLMBackend instance, str name, or None
        None -> TemplateBackend
        "template" -> TemplateBackend
        "gemini" -> GeminiBackend
        Instance -> used directly
    """
    backend = _resolve_backend(backend)

    request = build_request(report, question=question)
    response: LLMResponse = backend.generate(request)

    return Explanation(
        text=response.text,
        backend=response.backend,
        rule_ids_cited=response.rule_ids_cited,
        evidence_count=len(report.evidence),
        contradiction_count=len(report.contradictions),
    )
