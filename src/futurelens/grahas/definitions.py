"""
The nine grahas and their classical properties.

Includes:
  - Swiss Ephemeris planet IDs
  - Natural nature (benefic / malefic / neutral)
  - Combustion orbs (per Phaladeepika)
  - Exaltation and debilitation signs
  - Moolatrikona signs
  - Own signs
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrahaDefinition:
    name: str
    swe_id: int
    nature: str                       # BENEFIC / MALEFIC / NEUTRAL
    exaltation_sign: int | None       # 0..11 or None (Rahu/Ketu)
    debilitation_sign: int | None
    own_signs: tuple[int, ...]
    moolatrikona_sign: int | None
    combustion_orb_deg: float | None  # None for Sun/Moon/Rahu/Ketu


# Sign indices:
# 0=Aries, 1=Taurus, ..., 11=Pisces.
#
# Swiss Ephemeris planet IDs:
#   SUN       = 0
#   MOON      = 1
#   MERCURY   = 2
#   VENUS     = 3
#   MARS      = 4
#   JUPITER   = 5
#   SATURN    = 6
#   MEAN_NODE = 10
#   TRUE_NODE = 11
#
# Project convention:
#   nodes.type = TRUE
#
# Therefore Rahu uses Swiss Ephemeris TRUE_NODE (11).
# Ketu is derived as exactly 180 degrees from Rahu in the
# graha engine and is not independently calculated.
GRAHAS: tuple[GrahaDefinition, ...] = (
    GrahaDefinition(
        name="SUN",
        swe_id=0,
        nature="MALEFIC",
        exaltation_sign=0,
        debilitation_sign=6,
        own_signs=(4,),
        moolatrikona_sign=4,
        combustion_orb_deg=None,
    ),

    GrahaDefinition(
        name="MOON",
        swe_id=1,
        nature="BENEFIC",
        exaltation_sign=1,
        debilitation_sign=7,
        own_signs=(3,),
        moolatrikona_sign=1,
        combustion_orb_deg=None,
    ),

    GrahaDefinition(
        name="MARS",
        swe_id=4,
        nature="MALEFIC",
        exaltation_sign=9,
        debilitation_sign=3,
        own_signs=(0, 7),
        moolatrikona_sign=0,
        combustion_orb_deg=17.0,
    ),

    GrahaDefinition(
        name="MERCURY",
        swe_id=2,
        nature="NEUTRAL",
        exaltation_sign=5,
        debilitation_sign=11,
        own_signs=(2, 5),
        moolatrikona_sign=5,
        combustion_orb_deg=14.0,
    ),

    GrahaDefinition(
        name="JUPITER",
        swe_id=5,
        nature="BENEFIC",
        exaltation_sign=3,
        debilitation_sign=9,
        own_signs=(8, 11),
        moolatrikona_sign=8,
        combustion_orb_deg=11.0,
    ),

    GrahaDefinition(
        name="VENUS",
        swe_id=3,
        nature="BENEFIC",
        exaltation_sign=11,
        debilitation_sign=5,
        own_signs=(1, 6),
        moolatrikona_sign=6,
        combustion_orb_deg=10.0,
    ),

    GrahaDefinition(
        name="SATURN",
        swe_id=6,
        nature="MALEFIC",
        exaltation_sign=6,
        debilitation_sign=0,
        own_signs=(9, 10),
        moolatrikona_sign=10,
        combustion_orb_deg=15.0,
    ),

    # Project rulebook:
    # nodes.type = TRUE
    #
    # Swiss Ephemeris:
    # swe.TRUE_NODE = 11
    GrahaDefinition(
        name="RAHU",
        swe_id=11,
        nature="MALEFIC",
        exaltation_sign=None,
        debilitation_sign=None,
        own_signs=(),
        moolatrikona_sign=None,
        combustion_orb_deg=None,
    ),

    # Ketu is derived as Rahu + 180 degrees in grahas/engine.py.
    # The swe_id is retained for completeness of the nine-graha
    # definition table but is not independently used for calculation.
    GrahaDefinition(
        name="KETU",
        swe_id=11,
        nature="MALEFIC",
        exaltation_sign=None,
        debilitation_sign=None,
        own_signs=(),
        moolatrikona_sign=None,
        combustion_orb_deg=None,
    ),
)


GRAHA_BY_NAME: dict[str, GrahaDefinition] = {
    g.name: g for g in GRAHAS
}