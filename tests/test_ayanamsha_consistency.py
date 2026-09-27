"""
Regression tests for ayanamsha consistency.

These tests verify that:

1. The configured ayanamsha reaches the astronomical layer.
2. TRUE_CITRA and LAHIRI produce different sidereal positions.
3. The tropical Ascendant is independent of ayanamsha.
4. The sidereal Ascendant changes consistently with the planetary
   sidereal longitudes.
5. The same ayanamsha offset is applied across Ascendant and planets.
6. Both supported ayanamsha conventions can be used successfully.

The tests use a fixed birth chart so that accidental changes to
the astronomical convention are detected immediately.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from futurelens import cast_chart
from futurelens.conventions import Ayanamsha, Conventions


# ---------------------------------------------------------------------------
# Golden test input
# ---------------------------------------------------------------------------

BIRTH_DATETIME = datetime(
    1990,
    7,
    15,
    6,
    30,
    tzinfo=timezone.utc,
)

LATITUDE = 19.0760
LONGITUDE = 72.8777


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def cast_with_ayanamsha(ayanamsha: Ayanamsha):
    """Cast the fixed validation chart using the requested ayanamsha."""

    return cast_chart(
        BIRTH_DATETIME,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        conventions=Conventions(
            ayanamsha=ayanamsha,
        ),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_true_citra_is_applied():
    """TRUE_CITRA must be preserved in the resolved chart."""

    chart = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)

    assert chart.conventions.ayanamsha == Ayanamsha.TRUE_CITRA


def test_lahiri_is_applied():
    """LAHIRI must be preserved in the resolved chart."""

    chart = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    assert chart.conventions.ayanamsha == Ayanamsha.LAHIRI


def test_tropical_ascendant_is_independent_of_ayanamsha():
    """
    Ayanamsha changes the sidereal reference frame.

    It must NOT change the underlying tropical Ascendant.
    """

    true_citra = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)
    lahiri = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    assert true_citra.ascendant.tropical_longitude == pytest.approx(
        lahiri.ascendant.tropical_longitude,
        abs=1e-10,
    )


def test_sidereal_ascendant_changes_with_ayanamsha():
    """
    TRUE_CITRA and LAHIRI must produce different sidereal Ascendants.
    """

    true_citra = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)
    lahiri = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    assert (
        true_citra.ascendant.sidereal_longitude
        != pytest.approx(
            lahiri.ascendant.sidereal_longitude,
            abs=1e-10,
        )
    )


@pytest.mark.parametrize(
    "planet",
    [
        "SUN",
        "MOON",
        "MARS",
        "MERCURY",
        "JUPITER",
        "VENUS",
        "SATURN",
        "RAHU",
        "KETU",
    ],
)
def test_planetary_sidereal_longitude_changes_with_ayanamsha(planet: str):
    """
    Every sidereal planetary longitude must respond to the selected
    ayanamsha.
    """

    true_citra = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)
    lahiri = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    true_position = true_citra.grahas[planet].longitude
    lahiri_position = lahiri.grahas[planet].longitude

    assert true_position != pytest.approx(
        lahiri_position,
        abs=1e-10,
    )


def test_ayanamsha_offset_is_consistent_across_ascendant_and_planets():
    """
    The difference between TRUE_CITRA and LAHIRI should represent the
    same sidereal reference-frame shift across the Ascendant and
    planetary positions.

    This is one of the most important architectural tests in this
    module. It detects a situation where the Ascendant and planetary
    calculations accidentally use different ayanamsha conventions.
    """

    true_citra = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)
    lahiri = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    ascendant_difference = (
        true_citra.ascendant.sidereal_longitude
        - lahiri.ascendant.sidereal_longitude
    )

    planets = [
        "SUN",
        "MOON",
        "MARS",
        "MERCURY",
        "JUPITER",
        "VENUS",
        "SATURN",
        "RAHU",
        "KETU",
    ]

    for planet in planets:
        true_position = true_citra.grahas[planet].longitude
        lahiri_position = lahiri.grahas[planet].longitude

        difference = true_position - lahiri_position

        assert difference == pytest.approx(
            ascendant_difference,
            abs=1e-10,
        ), (
            f"Ayanamsha offset mismatch for {planet}: "
            f"expected {ascendant_difference}, "
            f"got {difference}"
        )


def test_expected_true_citra_values():
    """
    Golden regression values for the current TRUE_CITRA implementation.

    These values come from the validated astronomical calculation for:

        1990-07-15 06:30 UTC
        19.0760 N
        72.8777 E

    If these values change, the astronomical implementation or its
    convention has changed and should be reviewed deliberately.
    """

    chart = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)

    assert chart.ascendant.tropical_longitude == pytest.approx(
        192.52214876441747,
        abs=1e-10,
    )

    assert chart.ascendant.sidereal_longitude == pytest.approx(
        168.80891758111034,
        abs=1e-10,
    )

    assert chart.ascendant.ayanamsha == pytest.approx(
        23.709352922309904,
        abs=1e-10,
    )

    assert chart.grahas["SUN"].longitude == pytest.approx(
        88.8143183173911,
        abs=1e-10,
    )

    assert chart.grahas["MOON"].longitude == pytest.approx(
        356.33310830068655,
        abs=1e-10,
    )

    assert chart.grahas["SATURN"].longitude == pytest.approx(
        268.2673426135719,
        abs=1e-10,
    )


def test_true_citra_and_lahiri_expected_difference():
    """
    Golden regression for the currently observed TRUE_CITRA vs LAHIRI
    reference-frame difference.
    """

    true_citra = cast_with_ayanamsha(Ayanamsha.TRUE_CITRA)
    lahiri = cast_with_ayanamsha(Ayanamsha.LAHIRI)

    expected_difference = 0.015521461993614594

    ascendant_difference = (
        true_citra.ascendant.sidereal_longitude
        - lahiri.ascendant.sidereal_longitude
    )

    sun_difference = (
        true_citra.grahas["SUN"].longitude
        - lahiri.grahas["SUN"].longitude
    )

    moon_difference = (
        true_citra.grahas["MOON"].longitude
        - lahiri.grahas["MOON"].longitude
    )

    saturn_difference = (
        true_citra.grahas["SATURN"].longitude
        - lahiri.grahas["SATURN"].longitude
    )

    assert ascendant_difference == pytest.approx(
        expected_difference,
        abs=1e-10,
    )

    assert sun_difference == pytest.approx(
        expected_difference,
        abs=1e-10,
    )

    assert moon_difference == pytest.approx(
        expected_difference,
        abs=1e-10,
    )

    assert saturn_difference == pytest.approx(
        expected_difference,
        abs=1e-10,
    )
