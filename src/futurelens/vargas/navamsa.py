"""
Navamsa (D9) transform.

Each 30-degree rasi divides into nine navamsas of 3 degrees 20 minutes.
The D9 sign is computed algebraically as:

    d9_sign_index = (sign_index * 9 + navamsa_index) mod 12

where navamsa_index = floor(degree_in_sign / (30 / 9)).

This is equivalent to the classical movable / fixed / dual counting
rule (BPHS ch. 6):

  - movable signs (Aries, Cancer, Libra, Capricorn): count from self
  - fixed signs (Taurus, Leo, Scorpio, Aquarius): count from the 9th
  - dual signs (Gemini, Virgo, Sagittarius, Pisces): count from the 5th

D9 dignity reuses the D1 dignity tables applied to the D9 sign.
"""

from __future__ import annotations

from futurelens.grahas.dignity import dignity_label
from futurelens.grahas.formatting import sign_name
from futurelens.models.varga import VargaPosition, VargaReport


_DEGREES_PER_NAVAMSA = 30.0 / 9.0


def navamsa_sign_of(longitude: float) -> int:
    """
    Return the Navamsa (D9) sign index (0..11) for a sidereal
    longitude in degrees (0..360).
    """
    lon = longitude % 360.0
    sign_index = int(lon // 30.0)
    degree_in_sign = lon - sign_index * 30.0
    navamsa_index = int(degree_in_sign // _DEGREES_PER_NAVAMSA)
    # Guard against floating-point edge: if degree_in_sign lands
    # exactly on 30.0 due to rounding, navamsa_index would be 9.
    if navamsa_index >= 9:
        navamsa_index = 8
    return (sign_index * 9 + navamsa_index) % 12


def navamsa_longitude_of(longitude: float) -> float:
    """
    Return the D9 longitude (0..360) for a sidereal longitude.

    The D9 longitude preserves the fractional degree within the
    navamsa so D9 house placements remain meaningful.
    """
    lon = longitude % 360.0
    sign_index = int(lon // 30.0)
    degree_in_sign = lon - sign_index * 30.0
    navamsa_index = int(degree_in_sign // _DEGREES_PER_NAVAMSA)
    if navamsa_index >= 9:
        navamsa_index = 8
        degree_within_navamsa = _DEGREES_PER_NAVAMSA
    else:
        degree_within_navamsa = (
            degree_in_sign - navamsa_index * _DEGREES_PER_NAVAMSA
        )
    d9_sign_index = (sign_index * 9 + navamsa_index) % 12
    return d9_sign_index * 30.0 + degree_within_navamsa


def navamsa_of_chart(chart) -> VargaReport:
    """
    Compute the Navamsa (D9) chart for every graha in a natal chart.
    """
    positions: dict[str, VargaPosition] = {}

    for name, g in chart.grahas.items():
        d9_sign = navamsa_sign_of(g.longitude)
        d9_lon = navamsa_longitude_of(g.longitude)
        d9_degree_in_sign = d9_lon - d9_sign * 30.0

        positions[name] = VargaPosition(
            name=name,
            d1_longitude=g.longitude,
            d1_sign_index=g.sign_index,
            d1_dignity=dignity_label(name, g.sign_index),
            d9_sign_index=d9_sign,
            d9_sign_name=sign_name(d9_sign),
            d9_degree_in_sign=d9_degree_in_sign,
            d9_longitude=d9_lon,
            d9_dignity=dignity_label(name, d9_sign),
        )

    return VargaReport(
        varga="D9",
        name="NAVAMSA",
        positions=positions,
    )