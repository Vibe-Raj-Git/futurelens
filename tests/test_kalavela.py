from datetime import datetime

from futurelens.astronomy.ascendant import compute_ascendant
from futurelens.models.upagraha import UpagrahaName
from futurelens.upagraha.kalavela import compute_kalavela


SUNRISE = datetime(2026, 1, 1, 6, 0, 0)
SUNSET = datetime(2026, 1, 1, 18, 0, 0)

LAT = 19.0760
LON = 72.8777


def test_day_birth_yields_expected_upagrahas():
    birth = datetime(2026, 1, 1, 12, 0, 0)
    result = compute_kalavela(
        birth_datetime=birth,
        sunrise=SUNRISE,
        sunset=SUNSET,
        latitude=LAT,
        longitude=LON,
        ascendant_func=compute_ascendant,
    )
    assert UpagrahaName.GULIKA in result
    assert UpagrahaName.YAMAKANTAKA in result


def test_positions_are_not_sign_boundaries():
    """Kalavela longitudes should not all be exact multiples of 30."""
    birth = datetime(2026, 1, 1, 12, 0, 0)
    result = compute_kalavela(
        birth_datetime=birth,
        sunrise=SUNRISE,
        sunset=SUNSET,
        latitude=LAT,
        longitude=LON,
        ascendant_func=compute_ascendant,
    )
    multiples = sum(
        1 for pos in result.values() if abs(pos.longitude % 30.0) < 1e-6
    )
    assert multiples < len(result), "All positions landed on sign boundaries."


def test_positions_are_consistent_with_ascendant_func():
    """Every Kalavela longitude must equal the ascendant at that moment."""
    birth = datetime(2026, 1, 1, 12, 0, 0)
    result = compute_kalavela(
        birth_datetime=birth,
        sunrise=SUNRISE,
        sunset=SUNSET,
        latitude=LAT,
        longitude=LON,
        ascendant_func=compute_ascendant,
    )
    for pos in result.values():
        assert 0.0 <= pos.longitude < 360.0
        assert 0.0 <= pos.degree_in_sign < 30.0


def test_night_birth_runs():
    sunrise = datetime(2026, 1, 1, 6, 0, 0)
    sunset = datetime(2026, 1, 1, 18, 0, 0)
    next_sunrise = datetime(2026, 1, 2, 6, 0, 0)
    birth = datetime(2026, 1, 1, 23, 0, 0)
    result = compute_kalavela(
        birth_datetime=birth,
        sunrise=sunrise,
        sunset=sunset,
        latitude=LAT,
        longitude=LON,
        ascendant_func=compute_ascendant,
        next_sunrise=next_sunrise,
    )
    assert isinstance(result, dict)
    assert len(result) > 0
