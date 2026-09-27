"""
Nakshatra and pada derivation.

The 27 nakshatras divide the sidereal zodiac into 27 equal arcs of
13 degrees 20 minutes each. Each nakshatra has 4 padas of 3 degrees
20 minutes each. The pada index (1..4) determines the navamsa sign.

References:
  Classical: each nakshatra spans 13d20'.
  Vimshottari dasha lord sequence starts at Ashwini with Ketu.
"""

from __future__ import annotations

from dataclasses import dataclass


# --- Tables ---------------------------------------------------------------

NAKSHATRA_NAMES: tuple[str, ...] = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
)

# Vimshottari dasha lord sequence, starting at Ashwini.
NAKSHATRA_LORDS: tuple[str, ...] = (
    "KETU",    "VENUS",   "SUN",     "MOON",    "MARS",    "RAHU",
    "JUPITER", "SATURN",  "MERCURY", "KETU",    "VENUS",   "SUN",
    "MOON",    "MARS",    "RAHU",    "JUPITER", "SATURN",  "MERCURY",
    "KETU",    "VENUS",   "SUN",     "MOON",    "MARS",    "RAHU",
    "JUPITER", "SATURN",  "MERCURY",
)

NAKSHATRA_SIZE_DEG = 360.0 / 27.0    # 13.3333...
PADA_SIZE_DEG = NAKSHATRA_SIZE_DEG / 4.0  # 3.3333...


# --- Result type ----------------------------------------------------------

@dataclass(frozen=True)
class NakshatraPosition:
    """Derived nakshatra information for a sidereal longitude."""

    nakshatra_index: int      # 0..26
    nakshatra_name: str
    pada: int                 # 1..4
    degree_in_nakshatra: float
    vimshottari_lord: str


# --- Derivation -----------------------------------------------------------

def nakshatra_of(longitude: float) -> NakshatraPosition:
    """
    Given a sidereal longitude in [0, 360), return the nakshatra,
    pada, degree within the nakshatra, and Vimshottari lord.
    """
    if not 0.0 <= longitude < 360.0:
        raise ValueError(f"longitude must be in [0, 360); got {longitude}")

    index = int(longitude // NAKSHATRA_SIZE_DEG)
    index = min(index, 26)  # guard against floating point at 359.9999...

    degree_in = longitude - index * NAKSHATRA_SIZE_DEG
    pada = int(degree_in // PADA_SIZE_DEG) + 1
    pada = min(pada, 4)

    return NakshatraPosition(
        nakshatra_index=index,
        nakshatra_name=NAKSHATRA_NAMES[index],
        pada=pada,
        degree_in_nakshatra=degree_in,
        vimshottari_lord=NAKSHATRA_LORDS[index],
    )
