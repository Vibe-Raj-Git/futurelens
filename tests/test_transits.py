"""
Transit engine tests.

Verifies:

  - transit positions are computed for all nine grahas
  - house_from_lagna is correct for known cases
  - house_from_moon is correct
  - nakshatra distance is modular
  - Sade Sati detection
  - transit report can be called from a Chart
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.transits.engine import (
    SLOW_GRAHAS,
    _house_from_sign,
    _nakshatra_distance,
    compute_transits,
    is_slow_graha,
    saturn_sade_sati,
)


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777


# --- House arithmetic -----------------------------------------------------

def test_house_from_sign_same_sign():
    assert _house_from_sign(5, 5) == 1


def test_house_from_sign_next_sign():
    assert _house_from_sign(6, 5) == 2


def test_house_from_sign_wraps():
    assert _house_from_sign(0, 11) == 2


def test_house_from_sign_opposite():
    assert _house_from_sign(0, 6) == 7


def test_house_from_sign_range():
    for ref in range(12):
        for trans in range(12):
            h = _house_from_sign(trans, ref)
            assert 1 <= h <= 12


# --- Nakshatra distance ---------------------------------------------------

def test_nakshatra_distance_same():
    assert _nakshatra_distance(5, 5) == 0


def test_nakshatra_distance_next():
    assert _nakshatra_distance(5, 6) == 1


def test_nakshatra_distance_wraps():
    assert _nakshatra_distance(26, 0) == 1


def test_nakshatra_distance_12th():
    assert _nakshatra_distance(0, 26) == 26


# --- Sade Sati ------------------------------------------------------------

def test_sade_sati_active_when_saturn_in_same_nakshatra():
    assert saturn_sade_sati(transit_saturn_nakshatra=5, natal_moon_nakshatra=5) is True


def test_sade_sati_active_when_saturn_in_12th():
    assert saturn_sade_sati(transit_saturn_nakshatra=4, natal_moon_nakshatra=5) is True


def test_sade_sati_active_when_saturn_in_2nd():
    assert saturn_sade_sati(transit_saturn_nakshatra=6, natal_moon_nakshatra=5) is True


def test_sade_sati_inactive_when_saturn_far():
    assert saturn_sade_sati(transit_saturn_nakshatra=10, natal_moon_nakshatra=5) is False


# --- Slow graha -----------------------------------------------------------

def test_slow_grahas():
    assert is_slow_graha("SATURN")
    assert is_slow_graha("JUPITER")
    assert is_slow_graha("RAHU")
    assert is_slow_graha("KETU")
    assert not is_slow_graha("SUN")
    assert not is_slow_graha("MOON")


# --- Transit report -------------------------------------------------------

def test_transit_report_has_all_grahas():
    r = compute_transits(
        when=BIRTH,
        natal_ascendant_sign=4,
        natal_moon_sign=11,
        natal_moon_nakshatra_index=26,
    )
    expected = {"SUN", "MOON", "MARS", "MERCURY", "JUPITER",
                "VENUS", "SATURN", "RAHU", "KETU"}
    assert set(r.positions.keys()) == expected


def test_transit_house_range():
    r = compute_transits(
        when=BIRTH,
        natal_ascendant_sign=4,
        natal_moon_sign=11,
        natal_moon_nakshatra_index=26,
    )
    for name, pos in r.positions.items():
        assert 1 <= pos.house_from_lagna <= 12, name
        assert 1 <= pos.house_from_moon <= 12, name
        assert 0 <= pos.house_from_moon_nakshatra <= 26, name


def test_transit_from_chart_matches_direct_call():
    """Chart.transits_at() should produce the same result as compute_transits()."""
    chart = cast_chart(BIRTH, LAT, LON)
    direct = compute_transits(
        when=BIRTH,
        natal_ascendant_sign=chart.ascendant.sign_index,
        natal_moon_sign=chart.grahas["MOON"].sign_index,
        natal_moon_nakshatra_index=(
            chart.grahas["MOON"].nakshatra.nakshatra_index
        ),
    )
    via_chart = chart.transits_at(BIRTH)

    for name in direct.positions:
        assert abs(
            direct.positions[name].graha.longitude
            - via_chart.positions[name].graha.longitude
        ) < 1e-9


def test_transit_at_different_date():
    """Transit positions should differ between two dates."""
    chart = cast_chart(BIRTH, LAT, LON)

    later = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
    t_birth = chart.transits_at(BIRTH)
    t_later = chart.transits_at(later)

    # At least one slow graha should have moved.
    moved = False
    for name in SLOW_GRAHAS:
        if abs(
            t_birth.positions[name].graha.longitude
            - t_later.positions[name].graha.longitude
        ) > 1.0:
            moved = True
            break
    assert moved, "No slow graha moved between 1990 and 2026."


def test_transit_lagna_house_consistent_with_sign():
    chart = cast_chart(BIRTH, LAT, LON)
    r = chart.transits_at(BIRTH)
    for name, pos in r.positions.items():
        expected = ((pos.graha.sign_index - chart.ascendant.sign_index) % 12) + 1
        assert pos.house_from_lagna == expected
