"""
Transit engine.

Computes current positions of the nine grahas and derives transit
houses relative to a natal chart. Optionally annotates each transit
with the SAV bindu value for the sign it occupies.
"""

from __future__ import annotations

from datetime import datetime

from futurelens.astronomy.ephemeris import SwissEphemerisProvider
from futurelens.grahas.engine import compute_grahas
from futurelens.models.transit import TransitPosition, TransitReport


def _house_from_sign(transit_sign: int, reference_sign: int) -> int:
    return ((transit_sign - reference_sign) % 12) + 1


def _nakshatra_distance(from_nakshatra: int, to_nakshatra: int) -> int:
    return (to_nakshatra - from_nakshatra) % 27


def compute_transits(
    when: datetime,
    natal_ascendant_sign: int,
    natal_moon_sign: int,
    natal_moon_nakshatra_index: int,
    ephemeris: SwissEphemerisProvider | None = None,
    sav_bindus: tuple[int, ...] | None = None,
) -> TransitReport:
    """
    Compute transit positions for all nine grahas.

    If sav_bindus is provided (a tuple of 12 SAV values, one per
    sign), each transit is annotated with the bindu value for the
    sign it occupies and a strength label.
    """
    if ephemeris is None:
        ephemeris = SwissEphemerisProvider()

    grahas = compute_grahas(when, ephemeris=ephemeris)

    # Import strength label lazily to avoid circular import.
    from futurelens.ashtakavarga.engine import bindu_strength_label

    positions: dict[str, TransitPosition] = {}
    for name, pos in grahas.items():
        sav_value = None
        sav_label = None
        if sav_bindus is not None:
            sav_value = sav_bindus[pos.sign_index]
            sav_label = bindu_strength_label(sav_value)

        positions[name] = TransitPosition(
            graha=pos,
            house_from_lagna=_house_from_sign(
                pos.sign_index, natal_ascendant_sign
            ),
            house_from_moon=_house_from_sign(
                pos.sign_index, natal_moon_sign
            ),
            house_from_moon_nakshatra=_nakshatra_distance(
                natal_moon_nakshatra_index,
                pos.nakshatra.nakshatra_index,
            ),
            sav_bindus=sav_value,
            sav_strength=sav_label,
        )

    return TransitReport(when=when, positions=positions)


SLOW_GRAHAS = ("SATURN", "JUPITER", "RAHU", "KETU")


def is_slow_graha(name: str) -> bool:
    return name in SLOW_GRAHAS


def saturn_sade_sati(
    transit_saturn_nakshatra: int,
    natal_moon_nakshatra: int,
) -> bool:
    distance = (transit_saturn_nakshatra - natal_moon_nakshatra) % 27
    return distance in (26, 0, 1)
