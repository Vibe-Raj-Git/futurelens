"""
Shared formatting helpers for rule authors.

Rules use these to render astrological facts as plain English.
They are deliberately small and side-effect-free.
"""

from __future__ import annotations

from futurelens.grahas.dignity import (
    is_debilitated,
    is_exalted,
    is_moolatrikona,
    is_own_sign,
)


SIGN_NAMES: tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

_ORDINALS: dict[int, str] = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}


def ordinal(n: int) -> str:
    """1 -> '1st', 12 -> '12th'."""
    try:
        return _ORDINALS.get(int(n), f"{n}th")
    except (TypeError, ValueError):
        return str(n)


def sign_name(sign_index: int) -> str:
    """0 -> 'Aries', 11 -> 'Pisces'."""
    try:
        idx = int(sign_index)
        if 0 <= idx < 12:
            return SIGN_NAMES[idx]
    except (TypeError, ValueError):
        pass
    return f"sign {sign_index}"


def house_phrase(house_number) -> str:
    """2 -> 'the 2nd house'. Handles None and unknown values."""
    if house_number is None:
        return "an unknown house"
    try:
        return f"the {ordinal(int(house_number))} house"
    except (TypeError, ValueError):
        return f"house {house_number}"


def dignity_label(graha_name: str, sign_index: int) -> str:
    """
    Return a short label describing the graha's dignity in the given
    sign.

    Examples: 'exalted', 'moolatrikona', 'own sign', 'debilitated',
              'neutral dignity'.
    """
    if is_exalted(graha_name, sign_index):
        return "exalted"
    if is_moolatrikona(graha_name, sign_index):
        return "in its moolatrikona"
    if is_own_sign(graha_name, sign_index):
        return "in its own sign"
    if is_debilitated(graha_name, sign_index):
        return "debilitated"
    return "in a neutral sign"


_REASON_PHRASES = {
    "lord_in_dusthana": "a difficult placement",
    "lord_combust": "weakened by combustion",
    "lord_in_kendra_or_trikona": "a favourable placement",
    "benefic_or_neutral_placement": "a supportive placement",
    "significator_in_dusthana": "a difficult placement",
    "significator_combust": "weakened by combustion",
    "significator_in_wealth_house": "placed in a wealth house",
    "significator_in_career_house": "placed in a career house",
    "neutral_placement": "a neutral placement",
    "placement_in_dusthana": "a difficult placement",
    "placement_combust": "weakened by combustion",
    "placement_in_kendra_or_trikona": "a favourable placement",
    "placement_in_career_house": "placed in a career house",
    "placement_in_wealth_house": "placed in a wealth house",
    "placement_in_family_house": "placed in a family house",
}


def reason_phrase(reason_key: str) -> str:
    """Convert a rule's reason key into a short phrase."""
    if not reason_key:
        return "evaluated"
    return _REASON_PHRASES.get(
        reason_key, reason_key.replace("_", " ")
    )


# Verdict phrases used by family relationship and similar rules.
_VERDICT_PHRASES = {
    "strongly_supported": "strongly supported",
    "supported": "supported",
    "mixed_slight_positive": "mixed, slight positive",
    "mixed_slight_negative": "mixed, slight negative",
    "challenging": "challenging",
}


def verdict_phrase(verdict: str) -> str:
    """Convert a rule's verdict key into a short phrase."""
    return _VERDICT_PHRASES.get(verdict, verdict.replace("_", " "))
