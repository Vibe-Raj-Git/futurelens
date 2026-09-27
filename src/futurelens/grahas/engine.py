"""
Graha engine.

Computes sidereal longitudes, signs, nakshatras, retrograde and
combustion status for all nine grahas.

Uses Swiss Ephemeris as the ephemeris backend.
"""

from __future__ import annotations

from datetime import datetime

from futurelens.astronomy.ephemeris import SwissEphemerisProvider
from futurelens.grahas.definitions import GRAHAS, GRAHA_BY_NAME
from futurelens.grahas.nakshatra import nakshatra_of
from futurelens.models.graha import GrahaPosition


def _angular_distance(a: float, b: float) -> float:
    """Smallest angular separation between two longitudes, in [0, 180]."""
    diff = abs((a - b) % 360.0)
    return min(diff, 360.0 - diff)


def _is_combust(
    graha_name: str, graha_lon: float, sun_lon: float
) -> bool:
    """Combustion per Phaladeepika orbs."""
    definition = GRAHA_BY_NAME[graha_name]
    if definition.combustion_orb_deg is None:
        return False
    separation = _angular_distance(graha_lon, sun_lon)
    return separation < definition.combustion_orb_deg


def compute_grahas(
    when: datetime,
    ephemeris: SwissEphemerisProvider | None = None,
) -> dict[str, GrahaPosition]:
    """
    Compute positions for all nine grahas.

    Rahu is computed from Swiss Ephemeris with the mean node (true
    node should be selected via the ayanamsha_id if needed). Ketu is
    always 180 degrees from Rahu.

    Returns
    -------
    dict mapping graha name (SUN, MOON, ..., KETU) to GrahaPosition.
    """
    if ephemeris is None:
        ephemeris = SwissEphemerisProvider()

    # Compute the Sun first so we can use it for combustion checks.
    sun_lon, _, _ = ephemeris.planet_longitude(when, 0)

    results: dict[str, GrahaPosition] = {}

    for definition in GRAHAS:
        if definition.name == "KETU":
            # Ketu is always 180 degrees from Rahu.
            if "RAHU" not in results:
                raise RuntimeError("Ketu requested before Rahu.")
            rahu = results["RAHU"]
            ketu_lon = (rahu.longitude + 180.0) % 360.0
            sign_index = int(ketu_lon // 30)
            results["KETU"] = GrahaPosition(
                name="KETU",
                longitude=ketu_lon,
                sign_index=sign_index,
                degree_in_sign=ketu_lon - sign_index * 30.0,
                nakshatra=nakshatra_of(ketu_lon),
                retrograde=True,  # nodes are always retrograde by convention
                combust=False,
            )
            continue

        longitude, speed, retrograde = ephemeris.planet_longitude(
            when, definition.swe_id
        )

        # Rahu and Ketu are always treated as retrograde
        # by Vedic astrology convention.
        if definition.name == "RAHU":
            retrograde = True
        elif definition.name in ("SUN", "MOON"):
            retrograde = False

        sign_index = int(longitude // 30)
        degree_in_sign = longitude - sign_index * 30.0

        combust = _is_combust(definition.name, longitude, sun_lon)

        results[definition.name] = GrahaPosition(
            name=definition.name,
            longitude=longitude,
            sign_index=sign_index,
            degree_in_sign=degree_in_sign,
            nakshatra=nakshatra_of(longitude),
            retrograde=retrograde,
            combust=combust,
        )

    return results
