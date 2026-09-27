"""
Ascendant (Lagna) calculation.

Primary backend: Swiss Ephemeris via pyswisseph.

Correctness notes
-----------------
Swiss Ephemeris returns sidereal house angles directly when
swe.houses_ex() is called with FLG_SIDEREAL.

We therefore do NOT reconstruct the tropical ascendant by adding
the ayanamsha to the sidereal result.

Instead:

    1. Call swe.houses_ex() without FLG_SIDEREAL for the tropical
       ascendant and MC.

    2. Call swe.houses_ex() with FLG_SIDEREAL for the sidereal
       ascendant.

This avoids the double-subtraction/nutation issue encountered in
the earlier implementation.

Default ayanamsha
-----------------
The project default is Swiss Ephemeris SIDM_TRUE_CITRA.

This is the closest Swiss Ephemeris match to the JHora
True Lahiri / Chitrapaksha configuration used by this project.
The small residual difference is documented in the Rulebook.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


try:
    import swisseph as _swe  # type: ignore

    _HAS_SWE = True
except ImportError:
    _swe = None
    _HAS_SWE = False


DEFAULT_AYANAMSHA = "SIDM_TRUE_CITRA"


def _default_ayanamsha_id() -> int:
    """Return the Swiss Ephemeris ID for the project default."""
    if _swe is None:
        return 0

    return _swe.SIDM_TRUE_CITRA


@dataclass(frozen=True)
class AscendantResult:
    """Angles returned by the ascendant calculation."""

    tropical_longitude: float
    sidereal_longitude: float
    ayanamsha: float
    sign_index: int
    degree_in_sign: float
    ascendant_tropical: float
    mc_tropical: float
    backend: str


def compute_ascendant(
    when: datetime,
    latitude: float,
    longitude: float,
    *,
    sidereal: bool = True,
    ayanamsha_id: Optional[int] = None,
) -> AscendantResult:
    """
    Compute the ascendant for a birth moment.

    Parameters
    ----------
    when:
        Timezone-aware datetime. Naive datetimes are interpreted as UTC.

    latitude:
        Latitude in degrees, north positive.

    longitude:
        Longitude in degrees, east positive.

    sidereal:
        If True, calculate the sidereal ascendant using the supplied
        ayanamsha. The result always contains both tropical and
        sidereal longitudes.

    ayanamsha_id:
        Swiss Ephemeris SIDM_* ayanamsha ID.

        If omitted, SIDM_TRUE_CITRA is used.
    """

    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"Latitude out of range: {latitude}")

    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"Longitude out of range: {longitude}")

    if not _HAS_SWE:
        raise RuntimeError(
            "pyswisseph is required for the ascendant calculator. "
            "Install it with: pip install pyswisseph"
        )

    return _compute_via_swisseph(
        when=when,
        latitude=latitude,
        longitude=longitude,
        sidereal=sidereal,
        ayanamsha_id=ayanamsha_id,
    )


def _to_jd_ut(when: datetime) -> float:
    """Convert datetime to Swiss Ephemeris Julian Day UT."""

    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    when_utc = when.astimezone(timezone.utc)

    hour = (
        when_utc.hour
        + when_utc.minute / 60.0
        + when_utc.second / 3600.0
        + when_utc.microsecond / 3.6e9
    )

    return _swe.julday(
        when_utc.year,
        when_utc.month,
        when_utc.day,
        hour,
    )


def _compute_via_swisseph(
    when: datetime,
    latitude: float,
    longitude: float,
    sidereal: bool,
    ayanamsha_id: Optional[int],
) -> AscendantResult:
    """Compute tropical and sidereal ascendant natively in Swiss Ephemeris."""

    jd_ut = _to_jd_ut(when)

    # ------------------------------------------------------------------
    # Call 1: tropical ascendant and MC.
    # ------------------------------------------------------------------

    _, ascmc_tropical = _swe.houses_ex(
        jd_ut,
        latitude,
        longitude,
        b"P",
        0,
    )

    asc_tropical = ascmc_tropical[0] % 360.0
    mc_tropical = ascmc_tropical[1] % 360.0

    # ------------------------------------------------------------------
    # Call 2: sidereal ascendant.
    # ------------------------------------------------------------------

    if sidereal:
        ayan = (
            ayanamsha_id
            if ayanamsha_id is not None
            else _default_ayanamsha_id()
        )

        _swe.set_sid_mode(ayan)

        _, ascmc_sidereal = _swe.houses_ex(
            jd_ut,
            latitude,
            longitude,
            b"P",
            _swe.FLG_SIDEREAL,
        )

        asc_sidereal = ascmc_sidereal[0] % 360.0

        # Use Swiss Ephemeris's own value for reporting.
        ayan_value = _swe.get_ayanamsa_ut(jd_ut)

    else:
        asc_sidereal = asc_tropical
        ayan_value = 0.0

    sign_index = int(asc_sidereal // 30.0)
    degree_in_sign = (
        asc_sidereal - sign_index * 30.0
    )

    return AscendantResult(
        tropical_longitude=asc_tropical,
        sidereal_longitude=asc_sidereal,
        ayanamsha=ayan_value,
        sign_index=sign_index,
        degree_in_sign=degree_in_sign,
        ascendant_tropical=asc_tropical,
        mc_tropical=mc_tropical,
        backend="swisseph",
    )