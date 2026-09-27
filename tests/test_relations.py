"""Relations tests."""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.grahas.relations import (
    KENDRAS,
    TRIKONAS,
    DUSTHANAS,
    aspects,
    conjunct,
    exchange,
    graha_in_kendra_from_graha,
    house_from_house,
    is_dusthana,
    is_kendra,
    is_trikona,
    mutual_aspect,
)


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777


def test_kendra_predicate():
    assert is_kendra(1)
    assert is_kendra(4)
    assert is_kendra(7)
    assert is_kendra(10)
    assert not is_kendra(2)


def test_trikona_predicate():
    assert is_trikona(1)
    assert is_trikona(5)
    assert is_trikona(9)
    assert not is_trikona(2)


def test_dusthana_predicate():
    assert is_dusthana(6)
    assert is_dusthana(8)
    assert is_dusthana(12)
    assert not is_dusthana(1)


def test_house_from_house():
    assert house_from_house(1, 1) == 1
    assert house_from_house(1, 7) == 7
    assert house_from_house(4, 1) == 10


def test_conjunct_reflexive():
    chart = cast_chart(BIRTH, LAT, LON)
    assert conjunct(chart, "SUN", "SUN")


def test_aspects_reflexive_7th():
    """Every graha aspects its own 7th sign; verify against Jupiter."""
    chart = cast_chart(BIRTH, LAT, LON)
    jup = chart.grahas["JUPITER"]
    seventh_sign = (jup.sign_index + 6) % 12
    # Find a graha in that sign, if any.
    for name, pos in chart.grahas.items():
        if pos.sign_index == seventh_sign:
            assert aspects(chart, "JUPITER", name)
            break


def test_exchange_requires_mutual_ownership():
    """Exchange only for grahas that own each other's signs."""
    chart = cast_chart(BIRTH, LAT, LON)
    # Sun and Moon do not own signs in a way that supports exchange
    # with each other in most charts; this tests the function does not
    # crash on arbitrary pairs.
    result = exchange(chart, "SUN", "MOON")
    assert isinstance(result, bool)


def test_graha_in_kendra_from_graha():
    chart = cast_chart(BIRTH, LAT, LON)
    result = graha_in_kendra_from_graha(chart, "JUPITER", "MOON")
    assert isinstance(result, bool)
