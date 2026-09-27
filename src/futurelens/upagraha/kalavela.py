"""
Kalavela (time-based) Upagrahas, Phaladeepika ch. 25.

Day divided into 8 equal portions starting from the weekday lord.
Night divided into 8 equal portions starting from the lord of the
5th weekday (i.e., the 5th day counted from the current weekday).

Portion of Saturn  -> Gulika
Portion of Sun     -> Kala
Portion of Mars    -> Mrityu
Portion of Jupiter -> Yamakantaka
Portion of Mercury -> Ardhaprahara

Position rule
-------------
Each Upagraha's position is the ASCENDANT AT THE MOMENT ITS PORTION
BEGINS. The degree is the real ascendant degree at that moment, not
a sign boundary. This is the standard interpretation in Parashara's
Light, Jagannatha Hora, and other major Jyotish software.

The ascendant is computed by a caller-supplied function. This keeps
kalavela.py independent of any specific ephemeris backend.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from futurelens.models.upagraha import (
    UpagrahaFamily,
    UpagrahaName,
    UpagrahaPosition,
)


# --- Classical tables -----------------------------------------------------

PLANET_ORDER = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

WEEKDAY_LORD = {
    0: "MOON",     # Monday
    1: "MARS",     # Tuesday
    2: "MERCURY",  # Wednesday
    3: "JUPITER",  # Thursday
    4: "VENUS",    # Friday
    5: "SATURN",   # Saturday
    6: "SUN",      # Sunday
}

PORTION_UPAGRAHA = {
    "SATURN": UpagrahaName.GULIKA,
    "SUN": UpagrahaName.KALA,
    "MARS": UpagrahaName.MRITYU,
    "JUPITER": UpagrahaName.YAMAKANTAKA,
    "MERCURY": UpagrahaName.ARDHAPRAHARA,
}


# --- Portion lord logic ---------------------------------------------------

def _next_lord(lord: str) -> str:
    idx = PLANET_ORDER.index(lord)
    return PLANET_ORDER[(idx + 1) % len(PLANET_ORDER)]


def _portion_lords(start_lord: str, count: int) -> list[str | None]:
    """
    Portion lords for the day scheme.

    The 8th portion is lordless (classical rule).
    """
    lords: list[str | None] = []
    current = start_lord
    for i in range(count):
        if i == 7:
            lords.append(None)
        else:
            lords.append(current)
            current = _next_lord(current)
    return lords


# --- Ascendant type -------------------------------------------------------

# The ascendant function returns an object with a .sidereal_longitude
# attribute (in degrees, 0..360). We do not import the concrete
# AscendantResult type to keep this module decoupled.

AscendantFunc = Callable[[datetime, float, float], object]


def _ascendant_longitude(
    ascendant_func: AscendantFunc,
    when: datetime,
    latitude: float,
    longitude: float,
) -> float:
    """
    Call the ascendant function and return the sidereal longitude.
    """
    result = ascendant_func(when, latitude, longitude)
    return float(result.sidereal_longitude)


# --- Main computation -----------------------------------------------------

def compute_kalavela(
    birth_datetime: datetime,
    sunrise: datetime,
    sunset: datetime,
    latitude: float,
    longitude: float,
    ascendant_func: AscendantFunc,
    next_sunrise: datetime | None = None,
) -> dict[UpagrahaName, UpagrahaPosition]:
    """
    Compute Kalavela Upagraha positions.

    Each Upagraha's longitude is the real sidereal ascendant at the
    moment its portion begins.

    Parameters
    ----------
    birth_datetime : datetime
        The moment of birth.
    sunrise, sunset : datetime
        Sunrise and sunset for the astrological day containing the birth.
    latitude, longitude : float
        Birth location, needed to compute the ascendant.
    ascendant_func : callable(when, lat, lon) -> object with
                     .sidereal_longitude
        In production this is `futurelens.astronomy.ascendant.compute_ascendant`.
    next_sunrise : datetime, optional
        Required only when birth is at night (after sunset).

    Returns
    -------
    dict mapping UpagrahaName to UpagrahaPosition
    """
    is_day = sunrise <= birth_datetime < sunset

    if is_day:
        start, end = sunrise, sunset
        weekday = birth_datetime.weekday()
        start_lord = WEEKDAY_LORD[weekday]
    else:
        if next_sunrise is None:
            next_sunrise = sunset + timedelta(hours=12)
        start, end = sunset, next_sunrise
        weekday = birth_datetime.weekday()
        fifth_weekday = (weekday + 4) % 7
        start_lord = WEEKDAY_LORD[fifth_weekday]

    lords = _portion_lords(start_lord, 8)
    total_seconds = (end - start).total_seconds()
    portion_seconds = total_seconds / 8.0

    results: dict[UpagrahaName, UpagrahaPosition] = {}

    for i, lord in enumerate(lords):
        if lord is None:
            continue
        upagraha = PORTION_UPAGRAHA.get(lord)
        if upagraha is None:
            continue

        # The portion starts at this moment.
        portion_start = start + timedelta(seconds=portion_seconds * i)

        # Real sidereal ascendant at that moment.
        longitude_deg = _ascendant_longitude(
            ascendant_func, portion_start, latitude, longitude
        )
        sign_index = int(longitude_deg // 30)
        degree_in_sign = longitude_deg - sign_index * 30.0

        results[upagraha] = UpagrahaPosition(
            name=upagraha,
            family=UpagrahaFamily.KALAVELA,
            longitude=longitude_deg,
            sign_index=sign_index,
            degree_in_sign=degree_in_sign,
            house=None,  # filled in by the engine
        )

    return results
