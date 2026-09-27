"""Dignity tests."""

from futurelens.grahas.dignity import (
    dignity_label,
    is_debilitated,
    is_exalted,
    is_moolatrikona,
    is_own_sign,
    is_strong_in_sign,
)


def test_sun_exalted_in_aries():
    assert is_exalted("SUN", 0)


def test_sun_debilitated_in_libra():
    assert is_debilitated("SUN", 6)


def test_moon_exalted_in_taurus():
    assert is_exalted("MOON", 1)


def test_jupiter_own_sign():
    assert is_own_sign("JUPITER", 8)  # Sagittarius
    assert is_own_sign("JUPITER", 11)  # Pisces


def test_saturn_own_signs():
    assert is_own_sign("SATURN", 9)   # Capricorn
    assert is_own_sign("SATURN", 10)  # Aquarius


def test_venus_moolatrikona():
    assert is_moolatrikona("VENUS", 6)  # Libra


def test_strong_in_sign_combines():
    assert is_strong_in_sign("JUPITER", 8)
    assert is_strong_in_sign("SUN", 0)
    assert is_strong_in_sign("MOON", 1)


def test_dignity_label():
    assert dignity_label("SUN", 0) == "EXALTED"
    assert dignity_label("SUN", 6) == "DEBILITATED"
    assert dignity_label("JUPITER", 8) == "MOOLATRIKONA"
    assert dignity_label("JUPITER", 11) == "OWN_SIGN"
