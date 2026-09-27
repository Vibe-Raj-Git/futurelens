"""
Gochara engine tests.

Verifies:

  - the favourable/unfavourable tables
  - Vedha point lookups
  - the motion classifier
  - the SAV strength label
  - Sade Sati phase detection
  - the verdict computation logic
  - the end-to-end engine against the reference chart
"""

from datetime import datetime, timezone, timedelta

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens import cast_chart
from futurelens.gochara import compute_gochara
from futurelens.gochara.definitions import (
    GOCHARA_FAVOURABLE_FROM_MOON,
    SLOW_GRAHAS,
    VEDHA_POINTS,
    get_favourable_houses,
    is_favourable_from_lagna,
    is_favourable_from_moon,
    vedha_target_for,
)
from futurelens.gochara.engine import (
    GocharaReport,
    _motion_for,
    _sade_sati_phase,
    _sav_strength_label,
)
from futurelens.models.gochara import (
    GocharaMotion,
    GocharaTransit,
    GocharaVerdict,
    SadeSatiPhase,
)


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1984, 8, 30, 12, 2, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
TARGET = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------

def test_slow_grahas_are_four():
    assert SLOW_GRAHAS == ("JUPITER", "SATURN", "RAHU", "KETU")


def test_jupiter_favourable_houses():
    assert GOCHARA_FAVOURABLE_FROM_MOON["JUPITER"] == (2, 5, 7, 9, 11)


def test_saturn_favourable_houses():
    assert GOCHARA_FAVOURABLE_FROM_MOON["SATURN"] == (3, 6, 11)


def test_rahu_favourable_houses():
    assert GOCHARA_FAVOURABLE_FROM_MOON["RAHU"] == (3, 6, 10, 11)


def test_ketu_favourable_houses():
    assert GOCHARA_FAVOURABLE_FROM_MOON["KETU"] == (3, 6, 10, 11)


def test_get_favourable_houses_helper():
    assert get_favourable_houses("JUPITER") == (2, 5, 7, 9, 11)
    assert get_favourable_houses("UNKNOWN") == ()


def test_is_favourable_from_moon():
    assert is_favourable_from_moon("JUPITER", 5) is True
    assert is_favourable_from_moon("JUPITER", 6) is False
    assert is_favourable_from_moon("SATURN", 6) is True
    assert is_favourable_from_moon("SATURN", 5) is False


def test_is_favourable_from_lagna():
    assert is_favourable_from_lagna("JUPITER", 9) is True
    assert is_favourable_from_lagna("SATURN", 10) is False


# --------------------------------------------------------------------------
# Vedha
# --------------------------------------------------------------------------

def test_vedha_points_for_jupiter():
    assert VEDHA_POINTS["JUPITER"][2] == 12
    assert VEDHA_POINTS["JUPITER"][5] == 4
    assert VEDHA_POINTS["JUPITER"][7] == 3
    assert VEDHA_POINTS["JUPITER"][9] == 10
    assert VEDHA_POINTS["JUPITER"][11] == 8


def test_vedha_points_for_saturn():
    assert VEDHA_POINTS["SATURN"][3] == 9
    assert VEDHA_POINTS["SATURN"][6] == 12
    assert VEDHA_POINTS["SATURN"][11] == 5


def test_vedha_target_for_returns_house():
    assert vedha_target_for("JUPITER", 5) == 4
    assert vedha_target_for("SATURN", 11) == 5
    assert vedha_target_for("KETU", 10) == 6


def test_vedha_target_returns_none_for_unfavourable_house():
    # Jupiter in the 6th is not favourable, so no Vedha applies.
    assert vedha_target_for("JUPITER", 6) is None
    # Jupiter in the 3rd is not favourable.
    assert vedha_target_for("JUPITER", 3) is None


def test_vedha_target_returns_none_for_unknown_graha():
    assert vedha_target_for("MOON", 5) is None


# --------------------------------------------------------------------------
# Motion classifier
# --------------------------------------------------------------------------

def test_motion_rahu_always_retrograde():
    assert _motion_for("RAHU", 1.0) == GocharaMotion.RETROGRADE
    assert _motion_for("RAHU", -1.0) == GocharaMotion.RETROGRADE


def test_motion_ketu_always_retrograde():
    assert _motion_for("KETU", 1.0) == GocharaMotion.RETROGRADE


def test_motion_jupiter_negative_is_retrograde():
    assert _motion_for("JUPITER", -0.05) == GocharaMotion.RETROGRADE


def test_motion_jupiter_near_station():
    assert _motion_for("JUPITER", 0.01) == GocharaMotion.NEAR_STATION
    assert _motion_for("JUPITER", -0.01) == GocharaMotion.RETROGRADE
    assert _motion_for("JUPITER", 0.02) == GocharaMotion.NEAR_STATION


def test_motion_jupiter_direct():
    assert _motion_for("JUPITER", 0.18) == GocharaMotion.DIRECT
    assert _motion_for("SATURN", 0.10) == GocharaMotion.DIRECT


# --------------------------------------------------------------------------
# SAV strength
# --------------------------------------------------------------------------

def test_sav_strength_labels():
    assert _sav_strength_label(35) == "VERY_STRONG"
    assert _sav_strength_label(30) == "VERY_STRONG"
    assert _sav_strength_label(28) == "STRONG"
    assert _sav_strength_label(25) == "STRONG"
    assert _sav_strength_label(24) == "MODERATE"
    assert _sav_strength_label(20) == "MODERATE"
    assert _sav_strength_label(19) == "WEAK"
    assert _sav_strength_label(15) == "WEAK"
    assert _sav_strength_label(14) == "VERY_WEAK"
    assert _sav_strength_label(0) == "VERY_WEAK"


# --------------------------------------------------------------------------
# Sade Sati
# --------------------------------------------------------------------------

def test_sade_sati_only_for_saturn():
    assert _sade_sati_phase("JUPITER", 5, 5) is None
    assert _sade_sati_phase("RAHU", 5, 5) is None


def test_sade_sati_peak():
    assert _sade_sati_phase("SATURN", 5, 5) == SadeSatiPhase.PEAK


def test_sade_sati_rising():
    # Transit nakshatra 12th from natal Moon nakshatra.
    assert _sade_sati_phase("SATURN", 4, 5) == SadeSatiPhase.RISING


def test_sade_sati_setting():
    # Transit nakshatra 2nd from natal Moon nakshatra.
    assert _sade_sati_phase("SATURN", 6, 5) == SadeSatiPhase.SETTING


def test_sade_sati_wraparound_rising():
    # Natal Moon in nakshatra 0, transit in nakshatra 26 -> 12th.
    assert _sade_sati_phase("SATURN", 26, 0) == SadeSatiPhase.RISING


def test_sade_sati_not_active():
    # Transit nakshatra far from natal Moon nakshatra.
    assert _sade_sati_phase("SATURN", 15, 5) is None


# --------------------------------------------------------------------------
# End-to-end engine
# --------------------------------------------------------------------------

def test_engine_returns_report():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    assert isinstance(report, GocharaReport)


def test_engine_returns_four_transits():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    assert set(report.transits.keys()) == set(SLOW_GRAHAS)


def test_every_transit_has_required_fields():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    for graha, t in report.transits.items():
        assert isinstance(t, GocharaTransit)
        assert t.graha == graha
        assert 0 <= t.transit_sign <= 11
        assert 1 <= t.house_from_lagna <= 12
        assert 1 <= t.house_from_moon <= 12
        assert 0 <= t.transit_nakshatra <= 26
        assert 0 <= t.nakshatra_from_moon <= 26
        assert 0 <= t.sav_bindus <= 60
        assert t.motion in GocharaMotion
        assert t.base_verdict_from_moon in ("FAVOURABLE", "UNFAVOURABLE")
        assert t.base_verdict_from_lagna in ("FAVOURABLE", "UNFAVOURABLE")
        assert t.final_verdict in GocharaVerdict
        assert t.subject
        assert t.finding
        assert t.interpretation


def test_rahu_ketu_are_retrograde():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    assert report.transits["RAHU"].motion == GocharaMotion.RETROGRADE
    assert report.transits["KETU"].motion == GocharaMotion.RETROGRADE


def test_rahu_ketu_are_opposite_signs():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    rahu_sign = report.transits["RAHU"].transit_sign
    ketu_sign = report.transits["KETU"].transit_sign
    assert (rahu_sign - ketu_sign) % 12 == 6


def test_aspect_houses_are_in_range():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    for t in report.transits.values():
        for h in t.aspected_natal_houses:
            assert 1 <= h <= 12


def test_report_partitions_verdicts():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    total = (
        len(report.favourable())
        + len(report.unfavourable())
        + len(report.mixed())
    )
    assert total == len(report.transits)


def test_by_graha_lookup():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    assert report.by_graha("SATURN") is not None
    assert report.by_graha("SATURN").graha == "SATURN"
    assert report.by_graha("MOON") is None


def test_sade_sati_attached_only_to_saturn():
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    for graha, t in report.transits.items():
        if graha != "SATURN":
            assert t.sade_sati_phase is None


def test_reference_chart_jupiter_aspects_include_1_3_5():
    """
    Jupiter transiting Cancer (index 3) casts 5th, 7th, and 9th
    whole-sign aspects. From Cancer:
      5th aspect  -> sign 7 (Scorpio)
      7th aspect  -> sign 9 (Capricorn)
      9th aspect  -> sign 11 (Pisces)
    For a Scorpio ascendant (index 7):
      1st, 3rd, and 5th houses.
    """
    chart = cast_chart(when=BIRTH, latitude=22.7196, longitude=75.8577)
    report = compute_gochara(chart, TARGET)
    jupiter = report.transits["JUPITER"]
    assert jupiter.transit_sign == 3  # Cancer
    assert jupiter.aspected_natal_houses == (1, 3, 5)
