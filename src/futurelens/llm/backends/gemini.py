"""
Google Gemini backend.

Calls the Google Gemini API via the official google-genai SDK.
"""

from __future__ import annotations

import os
from pathlib import Path

from futurelens.llm.contract import LLMRequest, LLMResponse
from futurelens.llm.sanitize import sanitize_citations


# Default timeout for the Gemini API call, in milliseconds.
# The SDK accepts a timeout config in milliseconds.
DEFAULT_TIMEOUT_MS = 30_000


def _find_project_root() -> Path:
    """
    Walk up from this file until we find the directory that
    contains pyproject.toml. That is the project root.
    """
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: four levels up from the backends package.
    return here.parents[4]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return

    # Load from CWD first (if user is at project root).
    load_dotenv(override=False)

    # Also load from the project root explicitly.
    env_file = _find_project_root() / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=False)


class GeminiBackend:
    """LLM backend that calls Google Gemini."""

    name = "gemini"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        client=None,
        temperature: float = 0.3,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> None:
        _load_dotenv()

        self._model = model or os.environ.get(
            "GEMINI_MODEL", "gemini-2.5-flash"
        )
        self._temperature = temperature
        self._timeout_ms = timeout_ms
        self._client = client
        self._api_key = api_key

        if self._client is None:
            self._client = self._make_client()

    def _make_client(self):
        try:
            from google import genai  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "google-genai is not installed. "
                "Install it with: pip install google-genai  "
                "(or, if you installed FutureLens as a package: "
                'pip install -e ".[gemini]")'
            ) from exc

        key = self._api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file or set it in the environment. "
                f"Looked in: {_find_project_root() / '.env'}"
            )
        return genai.Client(api_key=key)

    def generate(self, request: LLMRequest) -> LLMResponse:
        # Build the config with system instruction, temperature, and
        # a bounded timeout.
        config = {
            "system_instruction": request.system_prompt,
            "temperature": self._temperature,
            "http_options": {"timeout": self._timeout_ms},
        }

        response = self._client.models.generate_content(
            model=self._model,
            contents=request.user_prompt,
            config=config,
        )

        raw_text = getattr(response, "text", None) or ""

        valid_ids = self._valid_rule_ids(request)
        sanitized = sanitize_citations(raw_text, valid_ids)

        return LLMResponse(
            text=sanitized.text,
            rule_ids_cited=sanitized.valid_cited,
            backend=self.name,
            raw={
                "valid_cited": list(sanitized.valid_cited),
                "redacted_cited": list(sanitized.redacted_cited),
                "redacted_count": len(sanitized.redacted_cited),
                "model": self._model,
                "timeout_ms": self._timeout_ms,
            },
        )

    def _valid_rule_ids(self, request: LLMRequest) -> set[str]:
        evidence = request.payload.get("evidence", [])
        return {e.get("rule_id") for e in evidence if e.get("rule_id")}