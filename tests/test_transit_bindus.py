"""Transit strength annotation tests."""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_transits_have_sav_bindus():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.transits_at(TARGET)
    for name, pos in report.positions.items():
        assert pos.sav_bindus is not None, name
        assert 0 <= pos.sav_bindus <= 60, name


def test_transits_have_sav_strength():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.transits_at(TARGET)
    valid = {"VERY_STRONG", "STRONG", "MODERATE", "WEAK", "VERY_WEAK"}
    for name, pos in report.positions.items():
        assert pos.sav_strength in valid, name


def test_transit_bindus_match_sav_for_sign():
    chart = cast_chart(BIRTH, LAT, LON)
    ashtaka = chart.ashtakavarga()
    report = chart.transits_at(TARGET)
    for name, pos in report.positions.items():
        expected = ashtaka.sav.bindus_by_sign[pos.graha.sign_index]
        assert pos.sav_bindus == expected, name
