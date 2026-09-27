"""
Nakshatra derivation tests.

The 27 nakshatras span 13d20' each. Each pada spans 3d20'.
Ashwini starts at 0 degrees Aries (0 total sidereal).
"""

import pytest

from futurelens.grahas.nakshatra import (
    NAKSHATRA_LORDS,
    NAKSHATRA_NAMES,
    NAKSHATRA_SIZE_DEG,
    PADA_SIZE_DEG,
    nakshatra_of,
)


def test_tables_have_27_entries():
    assert len(NAKSHATRA_NAMES) == 27
    assert len(NAKSHATRA_LORDS) == 27


def test_ashwini_at_zero():
    nk = nakshatra_of(0.0)
    assert nk.nakshatra_index == 0
    assert nk.nakshatra_name == "Ashwini"
    assert nk.pada == 1
    assert nk.vimshottari_lord == "KETU"


def test_ashwini_pada_2():
    nk = nakshatra_of(PADA_SIZE_DEG + 0.1)
    assert nk.pada == 2


def test_ashwini_pada_4():
    nk = nakshatra_of(3 * PADA_SIZE_DEG + 0.1)
    assert nk.pada == 4


def test_last_pada_of_ashwini():
    nk = nakshatra_of(NAKSHATRA_SIZE_DEG - 0.01)
    assert nk.nakshatra_index == 0
    assert nk.pada == 4


def test_bharani_starts():
    nk = nakshatra_of(NAKSHATRA_SIZE_DEG + 0.01)
    assert nk.nakshatra_index == 1
    assert nk.nakshatra_name == "Bharani"
    assert nk.vimshottari_lord == "VENUS"


def test_revati_is_last():
    nk = nakshatra_of(359.99)
    assert nk.nakshatra_index == 26
    assert nk.nakshatra_name == "Revati"


def test_all_nakshatras_reachable():
    """Every nakshatra index 0..26 is produced by exactly one longitude."""
    seen = set()
    for i in range(27):
        mid = i * NAKSHATRA_SIZE_DEG + NAKSHATRA_SIZE_DEG / 2
        nk = nakshatra_of(mid)
        assert nk.nakshatra_index == i
        seen.add(nk.nakshatra_index)
    assert seen == set(range(27))


def test_longitude_validation():
    with pytest.raises(ValueError):
        nakshatra_of(-1.0)
    with pytest.raises(ValueError):
        nakshatra_of(360.0)


def test_vimshottari_sequence_starts_with_ketu():
    assert NAKSHATRA_LORDS[0] == "KETU"
    assert NAKSHATRA_LORDS[1] == "VENUS"
    assert NAKSHATRA_LORDS[2] == "SUN"
    assert NAKSHATRA_LORDS[3] == "MOON"
    assert NAKSHATRA_LORDS[4] == "MARS"
