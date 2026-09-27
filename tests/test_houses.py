"""
Whole-sign house resolver tests.

The resolver is deterministic and classical. The tests verify:

  - the 1st house is the ascendant sign
  - houses follow zodiacal order
  - the lord of each house is the natural ruler of its sign
  - the mapping is consistent for all 12 ascendants
  - every sign appears exactly once as a house sign
  - every house number 1..12 appears exactly once
  - input validation
"""

import pytest

from futurelens.houses.resolver import (
    SIGN_LORDS,
    SIGNS,
    resolve_houses,
)


# --- Basic structure ------------------------------------------------------

def test_first_house_is_ascendant_sign():
    for asc in range(12):
        chart = resolve_houses(asc)
        assert chart.house_signs[1] == asc


def test_houses_follow_zodiacal_order():
    chart = resolve_houses(0)  # Aries ascendant
    for house in range(1, 13):
        expected_sign = (house - 1) % 12
        assert chart.house_signs[house] == expected_sign


def test_aries_ascendant_lords():
    chart = resolve_houses(0)
    expected = [
        "MARS", "VENUS", "MERCURY", "MOON", "SUN", "MERCURY",
        "VENUS", "MARS", "JUPITER", "SATURN", "SATURN", "JUPITER",
    ]
    for i, lord in enumerate(expected, start=1):
        assert chart.lord_of_house(i) == lord


def test_scorpio_ascendant_lords():
    """Scorpio (index 7): Mars, Jupiter, Saturn, Saturn, Jupiter, Mars,
    Venus, Mercury, Moon, Sun, Mercury, Venus."""
    chart = resolve_houses(7)
    expected = [
        "MARS", "JUPITER", "SATURN", "SATURN", "JUPITER", "MARS",
        "VENUS", "MERCURY", "MOON", "SUN", "MERCURY", "VENUS",
    ]
    for i, lord in enumerate(expected, start=1):
        assert chart.lord_of_house(i) == lord


def test_sagittarius_ascendant_lords():
    """Sagittarius (index 8): Jupiter, Saturn, Saturn, Jupiter, Mars,
    Venus, Mercury, Moon, Sun, Mercury, Venus, Mars."""
    chart = resolve_houses(8)
    expected = [
        "JUPITER", "SATURN", "SATURN", "JUPITER", "MARS", "VENUS",
        "MERCURY", "MOON", "SUN", "MERCURY", "VENUS", "MARS",
    ]
    for i, lord in enumerate(expected, start=1):
        assert chart.lord_of_house(i) == lord


# --- Invariants -----------------------------------------------------------

def test_every_sign_appears_exactly_once():
    for asc in range(12):
        chart = resolve_houses(asc)
        signs = set(chart.house_signs.values())
        assert signs == set(range(12))


def test_every_house_number_appears_exactly_once():
    for asc in range(12):
        chart = resolve_houses(asc)
        assert set(chart.house_signs.keys()) == set(range(1, 13))
        assert set(chart.house_lords.keys()) == set(range(1, 13))


def test_lords_match_sign_lords_table():
    for asc in range(12):
        chart = resolve_houses(asc)
        for house in range(1, 13):
            sign = chart.house_signs[house]
            assert chart.house_lords[house] == SIGN_LORDS[sign]


# --- Helpers --------------------------------------------------------------

def test_sign_name_of_house():
    chart = resolve_houses(0)
    assert chart.sign_name_of_house(1) == "Aries"
    assert chart.sign_name_of_house(2) == "Taurus"
    assert chart.sign_name_of_house(12) == "Pisces"


def test_house_of_sign():
    chart = resolve_houses(0)  # Aries rising
    assert chart.house_of_sign(0) == 1   # Aries -> 1st
    assert chart.house_of_sign(11) == 12  # Pisces -> 12th


def test_house_of_sign_scorpio_ascendant():
    chart = resolve_houses(7)  # Scorpio rising
    assert chart.house_of_sign(7) == 1    # Scorpio -> 1st
    assert chart.house_of_sign(0) == 6    # Aries -> 6th


# --- Input validation ----------------------------------------------------

def test_ascendant_sign_index_validation_low():
    with pytest.raises(ValueError):
        resolve_houses(-1)


def test_ascendant_sign_index_validation_high():
    with pytest.raises(ValueError):
        resolve_houses(12)


def test_sign_lords_table_has_twelve_entries():
    assert len(SIGN_LORDS) == 12
    assert len(SIGNS) == 12
