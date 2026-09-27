"""
Whole-sign house and house-lord resolver.

Given an ascendant sign index (0 = Aries), produce:

  - house_signs: {1..12} -> sign index
  - house_lords: {1..12} -> planet name

Method: whole-sign houses, per Parashara.

  The ascendant sign is the 1st house.
  Each subsequent sign is the next house, in zodiacal order.

  The lord of each house is the natural ruler of the sign
  occupying that house.

This is fully deterministic. No conventions to select, no
traditions to reconcile. The rule has been stable for centuries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# --------------------------------------------------------------------------
# Classical tables
# --------------------------------------------------------------------------

SIGNS: tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

SIGN_LORDS: tuple[str, ...] = (
    "MARS",       # Aries
    "VENUS",      # Taurus
    "MERCURY",    # Gemini
    "MOON",       # Cancer
    "SUN",        # Leo
    "MERCURY",    # Virgo
    "VENUS",      # Libra
    "MARS",       # Scorpio
    "JUPITER",    # Sagittarius
    "SATURN",     # Capricorn
    "SATURN",     # Aquarius
    "JUPITER",    # Pisces
)


# --------------------------------------------------------------------------
# Result type
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class HouseChart:
    """Whole-sign house chart for a given ascendant."""

    ascendant_sign_index: int
    house_signs: Dict[int, int]     # {1..12} -> sign index
    house_lords: Dict[int, str]     # {1..12} -> planet name

    def sign_of_house(self, house: int) -> int:
        return self.house_signs[house]

    def sign_name_of_house(self, house: int) -> str:
        return SIGNS[self.house_signs[house]]

    def lord_of_house(self, house: int) -> str:
        return self.house_lords[house]

    def house_of_sign(self, sign_index: int) -> int:
        """Which house a given sign occupies, for this ascendant."""
        for h, s in self.house_signs.items():
            if s == sign_index:
                return h
        raise ValueError(f"Sign index {sign_index} not in chart.")


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def resolve_houses(ascendant_sign_index: int) -> HouseChart:
    """
    Resolve whole-sign houses and lords for an ascendant.

    Parameters
    ----------
    ascendant_sign_index : int in [0, 11]
        0 = Aries, 1 = Taurus, ..., 11 = Pisces.

    Returns
    -------
    HouseChart
    """
    if not 0 <= ascendant_sign_index <= 11:
        raise ValueError(
            f"ascendant_sign_index must be in [0, 11]; "
            f"got {ascendant_sign_index}"
        )

    house_signs: Dict[int, int] = {}
    house_lords: Dict[int, str] = {}

    for house in range(1, 13):
        sign_index = (ascendant_sign_index + house - 1) % 12
        house_signs[house] = sign_index
        house_lords[house] = SIGN_LORDS[sign_index]

    return HouseChart(
        ascendant_sign_index=ascendant_sign_index,
        house_signs=house_signs,
        house_lords=house_lords,
    )
