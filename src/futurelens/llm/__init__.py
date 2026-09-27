from futurelens.llm.backends.base import LLMBackend
from futurelens.llm.backends.template import TemplateBackend
from futurelens.llm.contract import (
    FORBIDDEN_KEYS,
    LLMRequest,
    LLMResponse,
    assert_payload_safe,
)
from futurelens.llm.explainer import Explanation, explain
from futurelens.llm.prompt import SYSTEM_PROMPT, build_request

__all__ = [
    "DEFAULT_BACKEND",
    "Explanation",
    "FORBIDDEN_KEYS",
    "LLMBackend",
    "LLMRequest",
    "LLMResponse",
    "SYSTEM_PROMPT",
    "TemplateBackend",
    "assert_payload_safe",
    "build_request",
    "explain",
]

from futurelens.llm.sanitize import (
    UNVERIFIED_MARKER,
    SanitizeResult,
    sanitize_citations,
)
