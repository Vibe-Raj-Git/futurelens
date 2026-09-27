"""
Vimshottari Dasha definitions.

Total cycle: 120 years. Nine Mahadashas in fixed sequence, each
ruled by a planet. The sequence is the same as the NAKSHATRA_LORDS
cycle in the grahas module.

References:
  BPHS ch. 46 (Dasha)
  Phaladeepika ch. 15-19
"""

from __future__ import annotations

from dataclasses import dataclass


# The Vimshottari dasha lord sequence, in years.
# Order: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
DASHA_LORDS: tuple[str, ...] = (
    "KETU", "VENUS", "SUN", "MOON", "MARS",
    "RAHU", "JUPITER", "SATURN", "MERCURY",
)

DASHA_YEARS: dict[str, int] = {
    "KETU":    7,
    "VENUS":  20,
    "SUN":     6,
    "MOON":   10,
    "MARS":    7,
    "RAHU":   18,
    "JUPITER": 16,
    "SATURN": 19,
    "MERCURY": 17,
}

# Total should be 120 years.
assert sum(DASHA_YEARS.values()) == 120

# Nakshatra-to-lord mapping. Each planet rules 3 nakshatras.
# Nakshatra index 0..26 -> dasha lord at birth.
NAKSHATRA_TO_DASHA_LORD: tuple[str, ...] = (
    "KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY",
    "KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY",
    "KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY",
)

# Sidereal year in days. Most Jyotish software uses 365.25 days.
DAYS_PER_YEAR = 365.25


@dataclass(frozen=True)
class DashaPeriod:
    """A single dasha period at any level."""

    lord: str
    start_days: float    # days since birth
    end_days: float      # days since birth
    level: str           # "MAHADASHA", "ANTARDASHA", "PRATYANTARDASHA"
    parent_lord: str | None = None


def next_lord(lord: str) -> str:
    """Next lord in the Vimshottari sequence, cyclically."""
    idx = DASHA_LORDS.index(lord)
    return DASHA_LORDS[(idx + 1) % len(DASHA_LORDS)]
