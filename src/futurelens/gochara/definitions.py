"""
Classical Gochara definitions.

Gochara is the transit of a graha through the houses of the natal
chart. The primary reference frame is the natal Moon (Chandra
Lagna). The secondary frame is the natal ascendant.

The favourable and unfavourable house tables are from Phaladeepika
chapter 26 and BPHS chapter 34. Vedha is a cancellation rule: if a
graha transits a favourable house but another graha occupies the
Vedha point, the favourable effect is blocked.

Only the four slow grahas are used for domain forecasting:
Jupiter, Saturn, Rahu, Ketu. The fast grahas (Sun, Moon, Mars,
Mercury, Venus) matter for Muhurta and daily timing, not for
life-domain forecasts.
"""

from __future__ import annotations


SLOW_GRAHAS: tuple[str, ...] = ("JUPITER", "SATURN", "RAHU", "KETU")


# --------------------------------------------------------------------------
# Favourable houses from Chandra Lagna (the natal Moon sign).
#
# A graha transiting one of these houses produces a favourable
# result. Any other house is unfavourable.
#
# Source: Phaladeepika ch. 26; BPHS ch. 34.
# --------------------------------------------------------------------------

GOCHARA_FAVOURABLE_FROM_MOON: dict[str, tuple[int, ...]] = {
    "JUPITER": (2, 5, 7, 9, 11),
    "SATURN": (3, 6, 11),
    "RAHU": (3, 6, 10, 11),
    "KETU": (3, 6, 10, 11),
}


# The same table applies when counting from the Lagna. Some
# traditions argue the tables were only meant to be counted from
# the Moon. We compute both and report both, which lets the
# domain engine decide which to use.

GOCHARA_FAVOURABLE_FROM_LAGNA: dict[str, tuple[int, ...]] = dict(
    GOCHARA_FAVOURABLE_FROM_MOON
)


# --------------------------------------------------------------------------
# Vedha points.
#
# For each (graha, favourable_house), the Vedha point is the house
# counted from the Moon where another graha's presence cancels the
# favourable effect.
#
# Source: Jyotish Sara Sangraha; also used by Phaladeepika.
# --------------------------------------------------------------------------

VEDHA_POINTS: dict[str, dict[int, int]] = {
    "JUPITER": {
        2: 12,
        5: 4,
        7: 3,
        9: 10,
        11: 8,
    },
    "SATURN": {
        3: 9,
        6: 12,
        11: 5,
    },
    "RAHU": {
        3: 9,
        6: 12,
        10: 6,
        11: 5,
    },
    "KETU": {
        3: 9,
        6: 12,
        10: 6,
        11: 5,
    },
}


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------

def get_favourable_houses(graha: str) -> tuple[int, ...]:
    """Return the favourable houses from the Moon for a slow graha."""
    return GOCHARA_FAVOURABLE_FROM_MOON.get(graha, ())


def is_favourable_from_moon(graha: str, house: int) -> bool:
    """Is the transit of `graha` through `house` (from Moon) favourable?"""
    return house in GOCHARA_FAVOURABLE_FROM_MOON.get(graha, ())


def is_favourable_from_lagna(graha: str, house: int) -> bool:
    """Is the transit of `graha` through `house` (from Lagna) favourable?"""
    return house in GOCHARA_FAVOURABLE_FROM_LAGNA.get(graha, ())


def vedha_target_for(graha: str, favourable_house: int) -> int | None:
    """
    Return the Vedha point for a graha transiting a favourable house.

    Returns None if the graha has no Vedha rule for that house, or if
    the house is not one of the graha's favourable houses.
    """
    return VEDHA_POINTS.get(graha, {}).get(favourable_house)
