"""
Ascendant calculator tests.

External reference: Jagannatha Hora (True Lahiri / Chitrapaksha).

Reference chart:
  1990-07-15 12:00 IST = 06:30 UTC
  Mumbai (19.076 N, 72.8777 E)

Expected values:
  JHora tropical:  192.522211 deg (Libra 12 31 19.96)
  JHora sidereal:  168.812963 deg (Virgo 18 48 46.66)
  Swiss True Citra tropical:  192.522149 deg
  Swiss True Citra sidereal:  168.808918 deg

Tolerances:
  Tropical: 0.001 deg  (3.6 arcsec, catches gross errors)
  Sidereal: 0.01 deg   (36 arcsec, allows for the 15 arcsec
                        ayanamsha implementation difference
                        between JHora and Swiss Ephemeris)
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.astronomy.ascendant import compute_ascendant


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


REFERENCE_UTC = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
REFERENCE_LAT = 19.0760
REFERENCE_LON = 72.8777

JHORA_TROPICAL = 192.522211
JHORA_SIDEREAL = 168.812963

TROPICAL_TOL = 0.001    # 3.6 arcsec
SIDEREAL_TOL = 0.01     # 36 arcsec


# --- Input validation -----------------------------------------------------

def test_latitude_validation():
    when = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        compute_ascendant(when, latitude=100.0, longitude=0.0)


def test_longitude_validation():
    when = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        compute_ascendant(when, latitude=0.0, longitude=200.0)


# --- Structural sanity ----------------------------------------------------

def test_ascendant_returns_swisseph_backend():
    when = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = compute_ascendant(when, latitude=51.48, longitude=0.0)
    assert result.backend == "swisseph"


def test_ascendant_longitudes_in_range():
    when = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = compute_ascendant(when, latitude=51.48, longitude=0.0)
    assert 0.0 <= result.tropical_longitude < 360.0
    assert 0.0 <= result.sidereal_longitude < 360.0
    assert 0 <= result.sign_index <= 11


def test_sign_index_matches_sidereal_longitude():
    when = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = compute_ascendant(when, latitude=51.48, longitude=0.0)
    assert result.sign_index == int(result.sidereal_longitude // 30)


# --- Ayanamsha identity ---------------------------------------------------

def test_true_citra_ayanamsha():
    """
    Assert the ayanamsha is True Chitrapaksha, not Traditional
    Lahiri. The two differ by about 70 arcseconds at this epoch.

    True Citra at 1990-07-15 06:30 UTC is 23.7093...
    Traditional Lahiri at the same moment is 23.6898...
    """
    result = compute_ascendant(
        REFERENCE_UTC,
        latitude=REFERENCE_LAT,
        longitude=REFERENCE_LON,
    )
    expected_ayanamsha = 23.7093527795
    assert abs(result.ayanamsha - expected_ayanamsha) < 1e-5, (
        f"Expected True Citra ayanamsha {expected_ayanamsha:.10f}, "
        f"got {result.ayanamsha:.10f}. "
        f"Difference: "
        f"{abs(result.ayanamsha - expected_ayanamsha) * 3600:.2f} arcsec. "
        f"If this differs by about 70 arcsec, SIDM_LAHIRI is "
        f"being used instead of SIDM_TRUE_CITRA."
    )


# --- External validation against Jagannatha Hora --------------------------

def test_reference_chart_tropical_ascendant():
    """
    JHora reports 192.522211 deg tropical. Swiss Ephemeris
    True Citra gives 192.522149 deg. Difference: 0.22 arcsec.

    We use a tight tolerance for tropical because there is no
    ayanamsha involved.
    """
    result = compute_ascendant(
        REFERENCE_UTC,
        latitude=REFERENCE_LAT,
        longitude=REFERENCE_LON,
        sidereal=False,
    )
    diff = abs(result.tropical_longitude - JHORA_TROPICAL)
    assert diff < TROPICAL_TOL, (
        f"Tropical ascendant off by {diff * 3600:.2f} arcsec "
        f"from JHora. Got {result.tropical_longitude:.6f}, "
        f"expected {JHORA_TROPICAL:.6f}."
    )
    assert result.sign_index == 6  # Libra


def test_reference_chart_sidereal_ascendant():
    """
    JHora reports 168.812963 deg sidereal. Swiss Ephemeris
    True Citra gives 168.808918 deg. Difference: 14.6 arcsec.

    Tolerance is 0.01 deg (36 arcsec) to accommodate this
    ayanamsha implementation difference.
    """
    result = compute_ascendant(
        REFERENCE_UTC,
        latitude=REFERENCE_LAT,
        longitude=REFERENCE_LON,
        sidereal=True,
    )
    diff = abs(result.sidereal_longitude - JHORA_SIDEREAL)
    assert diff < SIDEREAL_TOL, (
        f"Sidereal ascendant off by {diff * 3600:.2f} arcsec "
        f"from JHora. Got {result.sidereal_longitude:.6f}, "
        f"expected {JHORA_SIDEREAL:.6f}. "
        f"If the difference is around 70 arcsec, SIDM_LAHIRI "
        f"is being used instead of SIDM_TRUE_CITRA."
    )
    assert result.sign_index == 5  # Virgo


# --- Regression test for the original bug --------------------------------

def test_sidereal_is_not_double_subtracted():
    """
    Regression test for the original bug.

    Before the fix, the sidereal ascendant was Leo 25 07
    (145.12 deg) instead of Virgo 18 48 (168.81 deg), because
    the ayanamsha was subtracted twice.

    This is a regression test for the specific failure mode.
    It hard-codes the expected astronomical value, but does
    not reference the JHora constants directly, so it remains
    valid independently of the external reference validation.
    """
    result = compute_ascendant(
        REFERENCE_UTC,
        latitude=REFERENCE_LAT,
        longitude=REFERENCE_LON,
        sidereal=True,
    )
    # Must be Virgo (index 5), not Leo (index 4).
    assert result.sign_index == 5, (
        f"Expected Virgo (sign_index 5), got {result.sign_index}. "
        f"If this is 4 (Leo), the double-subtraction bug is back."
    )
    # Must be near 168.81, not near 145.12.
    assert 168.7 < result.sidereal_longitude < 168.9, (
        f"Expected sidereal longitude near 168.81, got "
        f"{result.sidereal_longitude:.4f}. "
        f"If this is near 145.12 (Leo 25 07), the "
        f"double-subtraction bug is back."
    )


# --- Internal consistency -------------------------------------------------

def test_sidereal_and_tropical_both_populated():
    """
    Both longitudes should be populated regardless of the flag.
    The difference should be close to the ayanamsha (may differ
    by up to 1 arcminute due to nutation handling in Swiss
    Ephemeris's traditional sidereal house calculation).
    """
    result = compute_ascendant(
        REFERENCE_UTC,
        latitude=REFERENCE_LAT,
        longitude=REFERENCE_LON,
        sidereal=True,
    )
    delta = (result.tropical_longitude - result.sidereal_longitude) % 360.0
    assert abs(delta - result.ayanamsha) < 1.0 / 60.0
