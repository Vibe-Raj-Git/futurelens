"""
Citation sanitizer.

The LLM is instructed to cite rule IDs from the evidence payload,
but in practice it sometimes invents plausible-looking rule IDs.
This module provides a deterministic post-processor that replaces
unverified citations with a neutral marker.

Design principle: trust the evidence, verify the LLM. If a rule ID
appears in the response text but not in the evidence payload, it is
redacted. The user sees a clear marker instead of a fabricated
authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


RULE_ID_PATTERN = re.compile(r"\[([A-Z][A-Z0-9\-]+)\]")

UNVERIFIED_MARKER = "[unverified-citation]"


@dataclass(frozen=True)
class SanitizeResult:
    """The result of sanitizing a response text."""

    text: str
    valid_cited: tuple[str, ...]
    redacted_cited: tuple[str, ...]


def sanitize_citations(
    text: str,
    valid_rule_ids: set[str] | frozenset[str],
) -> SanitizeResult:
    """
    Replace citations to rule IDs not in valid_rule_ids with a marker.

    Preserves the surrounding text. Only the bracket token is
    replaced. Repeated citations to the same invalid ID are all
    replaced.

    Parameters
    ----------
    text : str
    valid_rule_ids : set of rule IDs permitted in the text

    Returns
    -------
    SanitizeResult with the sanitized text, the set of valid IDs
    that appeared, and the set of invalid IDs that were redacted.
    """
    valid_set = set(valid_rule_ids)
    seen_valid: set[str] = set()
    seen_invalid: set[str] = set()

    def replace(match: re.Match) -> str:
        rid = match.group(1)
        if rid in valid_set:
            seen_valid.add(rid)
            return match.group(0)
        seen_invalid.add(rid)
        return UNVERIFIED_MARKER

    sanitized = RULE_ID_PATTERN.sub(replace, text)

    return SanitizeResult(
        text=sanitized,
        valid_cited=tuple(sorted(seen_valid)),
        redacted_cited=tuple(sorted(seen_invalid)),
    )
