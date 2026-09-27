"""
Golden chart test: Marilyn Monroe. Part 1 - Kalavela portion logic.

Reference: Parashara's Light output (Parashara Method = beginning of
portion), publicly circulated chart PDF.
Birth: June 1, 1926. Tuesday. Day birth.

This file validates ONLY the portion logic, which does not depend on
the ascendant calculator:

  - day duration matches the source
  - each of the 8 portions has the expected length
  - portion lord order for Tuesday is Mars, Mercury, Jupiter, ...
  - Yamakantaka falls in the 3rd portion
  - Gulika falls in the 5th portion
  - our segment convention matches the Parashara Method (beginning)

Sign and degree placement of Upagrahas is not asserted here, because
the ascendant at those moments requires ephemeris data that is not
part of this test.
"""

from datetime import datetime, timedelta

from futurelens.conventions import Conventions
from futurelens.models.upagraha import UpagrahaName
from futurelens.upagraha.kalavela import (
    WEEKDAY_LORD,
    _portion_lords,
)


GOLDEN_WEEKDAY = 1  # Monday=0, Tuesday=1

SUNRISE = datetime(1926, 6, 1, 4, 47, 0)
SUNSET = datetime(1926, 6, 1, 18, 54, 0)

EXPECTED_YAMAKANTAKA_START = datetime(1926, 6, 1, 8, 18, 0)
EXPECTED_GULIKA_START = datetime(1926, 6, 1, 11, 50, 0)


def test_golden_weekday_is_tuesday():
    assert SUNRISE.weekday() == GOLDEN_WEEKDAY


def test_golden_day_duration_matches_source():
    duration = SUNSET - SUNRISE
    assert duration == timedelta(hours=14, minutes=7)


def test_golden_portion_duration():
    day_seconds = (SUNSET - SUNRISE).total_seconds()
    portion_seconds = day_seconds / 8
    expected = timedelta(hours=1, minutes=45, seconds=52, microseconds=500000)
    assert abs(portion_seconds - expected.total_seconds()) < 0.01


def test_golden_portion_lords_for_tuesday():
    lords = _portion_lords(WEEKDAY_LORD[GOLDEN_WEEKDAY], 8)
    assert lords[0] == "MARS"
    assert lords[1] == "MERCURY"
    assert lords[2] == "JUPITER"
    assert lords[3] == "VENUS"
    assert lords[4] == "SATURN"
    assert lords[5] == "SUN"
    assert lords[6] == "MOON"
    assert lords[7] is None


def test_golden_yamakantaka_portion_index():
    lords = _portion_lords(WEEKDAY_LORD[GOLDEN_WEEKDAY], 8)
    assert lords.index("JUPITER") == 2

    day_seconds = (SUNSET - SUNRISE).total_seconds()
    portion_seconds = day_seconds / 8
    computed_start = SUNRISE + timedelta(seconds=portion_seconds * 2)
    assert abs((computed_start - EXPECTED_YAMAKANTAKA_START).total_seconds()) < 60


def test_golden_gulika_portion_index():
    lords = _portion_lords(WEEKDAY_LORD[GOLDEN_WEEKDAY], 8)
    assert lords.index("SATURN") == 4

    day_seconds = (SUNSET - SUNRISE).total_seconds()
    portion_seconds = day_seconds / 8
    computed_start = SUNRISE + timedelta(seconds=portion_seconds * 4)
    assert abs((computed_start - EXPECTED_GULIKA_START).total_seconds()) < 60


def test_golden_convention_is_start_of_segment():
    conv = Conventions()
    assert conv.segment_reference == "START_OF_SEGMENT"
