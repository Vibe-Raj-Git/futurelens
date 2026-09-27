"""
Weighting helper.

Computes the astrological importance tier of an evidence item
based on the specific facts of the placement.

The tiers follow the classical hierarchy:

  STRUCTURAL - the fundamental promise of the chart
  SUPPORTING - secondary strength or qualification
  MODIFIER   - adjustment at the margins
"""

from __future__ import annotations

from futurelens.grahas.dignity import (
    is_debilitated,
    is_exalted,
    is_moolatrikona,
    is_own_sign,
)
from futurelens.models.evidence import Weight


def weight_for_house_lord(
    lord_name: str,
    lord_sign: int,
    lord_house: int | None,
    lord_combust: bool,
    lord_rules_another_wealth_house: bool = False,
) -> Weight:
    """
    Weight for a WEALTH/CAREER/FAMILY-HOUSE-LORD-NATAL-001 item.

    STRUCTURAL - lord in own/exalted/moolatrikona sign, and rules
        another wealth house (Dhana Yoga candidate), or the lord
        of the 1st house placed strongly.

    SUPPORTING - lord in a favourable sign or placed in a kendra
        or trikona without being weakened.

    MODIFIER - lord in a dusthana, combust, or debilitated.
    """
    strong_sign = (
        is_own_sign(lord_name, lord_sign)
        or is_exalted(lord_name, lord_sign)
        or is_moolatrikona(lord_name, lord_sign)
    )

    if lord_combust or is_debilitated(lord_name, lord_sign):
        return Weight.MODIFIER

    if lord_house is None:
        return Weight.MODIFIER

    # Own/exalted sign plus rulership of another wealth house is
    # the structural Dhana Yoga signature.
    if strong_sign and lord_rules_another_wealth_house:
        return Weight.STRUCTURAL

    # Own/exalted sign alone is a strong structural feature when
    # the lord sits in a beneficial house.
    if strong_sign and lord_house in (1, 2, 4, 5, 7, 9, 10, 11):
        return Weight.STRUCTURAL

    # Any dusthana placement downgrades to MODIFIER.
    if lord_house in (6, 8, 12):
        return Weight.MODIFIER

    # Kendra or trikona placement with reasonable dignity.
    if lord_house in (1, 4, 5, 7, 9, 10):
        return Weight.SUPPORTING

    return Weight.SUPPORTING


def weight_for_significator(
    graha_name: str,
    graha_sign: int,
    graha_house: int | None,
    graha_combust: bool,
) -> Weight:
    """
    Weight for a WEALTH/CAREER/FAMILY-SIGNIFICATOR-NATAL-001 item.

    Jupiter in own sign in a wealth house is STRUCTURAL.
    Other significators in their own or exalted signs in a
    favourable house are SUPPORTING.
    Combust or debilitated significators are MODIFIERs.
    """
    if graha_combust or is_debilitated(graha_name, graha_sign):
        return Weight.MODIFIER

    strong_sign = (
        is_own_sign(graha_name, graha_sign)
        or is_exalted(graha_name, graha_sign)
        or is_moolatrikona(graha_name, graha_sign)
    )

    if graha_house is None:
        return Weight.MODIFIER

    if strong_sign and graha_house in (1, 2, 4, 5, 7, 9, 10, 11):
        # Jupiter in own sign in its own house is the classic
        # Dhana Yoga candidate.
        if graha_name == "JUPITER" and graha_house in (2, 5, 9, 11):
            return Weight.STRUCTURAL
        return Weight.SUPPORTING

    if graha_house in (6, 8, 12):
        return Weight.MODIFIER

    return Weight.SUPPORTING


def weight_for_dasha() -> Weight:
    """Dasha activation is timing, always SUPPORTING."""
    return Weight.SUPPORTING


def weight_for_transit() -> Weight:
    """Transits are temporal, always MODIFIER."""
    return Weight.MODIFIER


def weight_for_upagraha() -> Weight:
    """Upagrahas are subtle modifiers. Always MODIFIER."""
    return Weight.MODIFIER
