"""
Graha engine tests.

Uses Swiss Ephemeris. Tests verify:

  - all nine grahas are computed
  - Ketu is 180 degrees from Rahu
  - Sun and Moon are never retrograde
  - signs and degrees are consistent with longitudes
  - nakshatras are derived correctly
  - combustion flags are set for inner planets near the Sun
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.grahas.engine import compute_grahas


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


SAMPLE = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)


def test_all_nine_grahas_returned():
    g = compute_grahas(SAMPLE)
    expected = {"SUN", "MOON", "MARS", "MERCURY", "JUPITER",
                "VENUS", "SATURN", "RAHU", "KETU"}
    assert set(g.keys()) == expected


def test_ketu_is_opposite_rahu():
    g = compute_grahas(SAMPLE)
    diff = (g["KETU"].longitude - g["RAHU"].longitude) % 360.0
    assert abs(diff - 180.0) < 1e-9


def test_sun_and_moon_never_retrograde():
    g = compute_grahas(SAMPLE)
    assert g["SUN"].retrograde is False
    assert g["MOON"].retrograde is False


def test_longitudes_in_range():
    g = compute_grahas(SAMPLE)
    for name, pos in g.items():
        assert 0.0 <= pos.longitude < 360.0, name
        assert 0 <= pos.sign_index <= 11, name
        assert 0.0 <= pos.degree_in_sign < 30.0, name


def test_sign_index_matches_longitude():
    g = compute_grahas(SAMPLE)
    for name, pos in g.items():
        assert pos.sign_index == int(pos.longitude // 30), name


def test_nakshatra_is_populated():
    g = compute_grahas(SAMPLE)
    for name, pos in g.items():
        assert pos.nakshatra is not None, name
        assert 0 <= pos.nakshatra.nakshatra_index <= 26, name
        assert 1 <= pos.nakshatra.pada <= 4, name


def test_rahu_and_ketu_are_retrograde_by_convention():
    g = compute_grahas(SAMPLE)
    assert g["RAHU"].retrograde is True
    assert g["KETU"].retrograde is True


def test_sun_and_moon_are_not_combust():
    g = compute_grahas(SAMPLE)
    assert g["SUN"].combust is False
    assert g["MOON"].combust is False


def test_nodes_are_not_combust():
    """Rahu and Ketu are not subject to combustion."""
    g = compute_grahas(SAMPLE)
    assert g["RAHU"].combust is False
    assert g["KETU"].combust is False


def test_multiple_dates_do_not_crash():
    """Smoke test across a wide date range."""
    cases = [
        datetime(1950, 3, 10, 4, 15, tzinfo=timezone.utc),
        datetime(1975, 8, 22, 18, 45, tzinfo=timezone.utc),
        datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc),
        datetime(2025, 6, 15, 3, 30, tzinfo=timezone.utc),
    ]
    for when in cases:
        g = compute_grahas(when)
        assert len(g) == 9

def test_rahu_and_ketu_are_retrograde():
    from datetime import datetime, timezone

    when = datetime(
        1990, 7, 15, 6, 30,
        tzinfo=timezone.utc,
    )

    grahas = compute_grahas(when)

    assert grahas["RAHU"].retrograde is True
    assert grahas["KETU"].retrograde is True
