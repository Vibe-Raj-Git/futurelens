"""
End-to-end chart entry point tests.

These tests call cast_chart() with real birth data and verify that
the resulting Chart is internally consistent.
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.conventions import Conventions, UpagrahaEnumeration
from futurelens.models.upagraha import UpagrahaName


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


SAMPLE_BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
SAMPLE_LAT = 19.0760
SAMPLE_LON = 72.8777


# --- Basic construction ---------------------------------------------------

def test_cast_chart_returns_chart():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    assert chart is not None


def test_first_house_sign_equals_ascendant_sign():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    assert chart.houses.house_signs[1] == chart.ascendant.sign_index


def test_ascendant_sign_index_in_range():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    assert 0 <= chart.ascendant.sign_index <= 11


def test_sun_longitude_in_range():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    assert 0.0 <= chart.sun_longitude < 360.0


def test_all_nine_grahas_in_chart():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    expected = {"SUN", "MOON", "MARS", "MERCURY", "JUPITER",
                "VENUS", "SATURN", "RAHU", "KETU"}
    assert set(chart.grahas.keys()) == expected


def test_graha_houses_are_populated():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    for name, pos in chart.grahas.items():
        assert pos.house is not None, name
        assert 1 <= pos.house <= 12, name


# --- Sunrise and sunset ---------------------------------------------------

def test_sunrise_before_sunset():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    assert chart.sunrise < chart.sunset


# --- Upagrahas ------------------------------------------------------------

def test_sun_derived_upagrahas_present():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    for name in (
        UpagrahaName.DHUMA,
        UpagrahaName.VYATIPATA,
        UpagrahaName.PARIVESHA,
        UpagrahaName.INDRACHAPA,
        UpagrahaName.UPAKETU,
    ):
        assert name in chart.upagrahas.positions


def test_kalavela_upagrahas_present_default_profile():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    for name in (
        UpagrahaName.GULIKA,
        UpagrahaName.YAMAKANTAKA,
        UpagrahaName.KALA,
        UpagrahaName.ARDHAPRAHARA,
    ):
        assert name in chart.upagrahas.positions


def test_mrityu_present_in_extended_profile():
    chart = cast_chart(
        SAMPLE_BIRTH,
        SAMPLE_LAT,
        SAMPLE_LON,
        conventions=Conventions(
            upagraha_enumeration=UpagrahaEnumeration.EXTENDED_KALAVELA,
        ),
    )
    assert UpagrahaName.MRITYU in chart.upagrahas.positions


def test_upagraha_house_assignment_is_consistent():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    for name, pos in chart.upagrahas.positions.items():
        if pos.house is None:
            continue
        assert chart.houses.house_signs[pos.house] == pos.sign_index


# --- Validation -----------------------------------------------------------

def test_cast_chart_rejects_bad_latitude():
    with pytest.raises(ValueError):
        cast_chart(SAMPLE_BIRTH, latitude=100.0, longitude=0.0)


def test_cast_chart_rejects_bad_longitude():
    with pytest.raises(ValueError):
        cast_chart(SAMPLE_BIRTH, latitude=0.0, longitude=200.0)


# --- Convenience methods --------------------------------------------------

def test_house_of_longitude_method():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    house = chart.house_of_longitude(chart.sun_longitude)
    assert 1 <= house <= 12


def test_house_of_graha_method():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    house = chart.house_of_graha("SUN")
    assert 1 <= house <= 12


def test_house_of_upagraha_method():
    chart = cast_chart(SAMPLE_BIRTH, SAMPLE_LAT, SAMPLE_LON)
    house = chart.house_of_upagraha(UpagrahaName.GULIKA)
    assert house is None or 1 <= house <= 12
