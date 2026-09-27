"""
Backend registry.

Maps backend names to factory functions so explain() can accept a
string like "gemini" or "template" instead of an instance.
"""

from __future__ import annotations

from typing import Callable

from futurelens.llm.backends.template import TemplateBackend


_REGISTRY: dict[str, Callable[[], object]] = {}


def _register_defaults() -> None:
    if "template" not in _REGISTRY:
        _REGISTRY["template"] = lambda: TemplateBackend()


def _gemini_available() -> bool:
    """
    Return True if the Gemini backend can be imported.

    Importing the module here does not construct a client and does
    not read GEMINI_API_KEY. It only checks that the module and its
    dependencies are present.
    """
    try:
        from futurelens.llm.backends import gemini  # noqa: F401
    except Exception:
        return False
    return True


def register(name: str, factory: Callable[[], object]) -> None:
    """Register a backend factory under a name."""
    _REGISTRY[name] = factory


def get(name: str):
    """Get a backend instance by name."""
    _register_defaults()

    if name == "gemini":
        try:
            from futurelens.llm.backends.gemini import GeminiBackend
        except Exception as exc:
            raise ValueError(
                f"Gemini backend is not available in this environment: {exc}. "
                f"Install the optional dependency with: "
                f"pip install google-genai"
            ) from exc
        return GeminiBackend()

    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown backend: {name}. "
            f"Available: {available()}"
        )
    return _REGISTRY[name]()


def available() -> list[str]:
    """Return the list of backend names usable in this environment."""
    _register_defaults()
    names = set(_REGISTRY)
    if _gemini_available():
        names.add("gemini")
    return sorted(names)