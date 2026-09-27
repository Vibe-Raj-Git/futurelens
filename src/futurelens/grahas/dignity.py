"""
Planetary dignity lookup.

Exaltation, debilitation, moolatrikona, and own-sign status.
"""

from __future__ import annotations

from futurelens.grahas.definitions import GRAHA_BY_NAME


def is_exalted(graha_name: str, sign_index: int) -> bool:
    d = GRAHA_BY_NAME.get(graha_name)
    if d is None or d.exaltation_sign is None:
        return False
    return d.exaltation_sign == sign_index


def is_debilitated(graha_name: str, sign_index: int) -> bool:
    d = GRAHA_BY_NAME.get(graha_name)
    if d is None or d.debilitation_sign is None:
        return False
    return d.debilitation_sign == sign_index


def is_own_sign(graha_name: str, sign_index: int) -> bool:
    d = GRAHA_BY_NAME.get(graha_name)
    if d is None:
        return False
    return sign_index in d.own_signs


def is_moolatrikona(graha_name: str, sign_index: int) -> bool:
    d = GRAHA_BY_NAME.get(graha_name)
    if d is None or d.moolatrikona_sign is None:
        return False
    return d.moolatrikona_sign == sign_index


def is_strong_in_sign(graha_name: str, sign_index: int) -> bool:
    """True if the graha is exalted, moolatrikona, or in own sign."""
    return (
        is_exalted(graha_name, sign_index)
        or is_moolatrikona(graha_name, sign_index)
        or is_own_sign(graha_name, sign_index)
    )


def dignity_label(graha_name: str, sign_index: int) -> str:
    if is_exalted(graha_name, sign_index):
        return "EXALTED"
    if is_moolatrikona(graha_name, sign_index):
        return "MOOLATRIKONA"
    if is_own_sign(graha_name, sign_index):
        return "OWN_SIGN"
    if is_debilitated(graha_name, sign_index):
        return "DEBILITATED"
    return "NEUTRAL"
