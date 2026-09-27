"""Ashtakavarga tests."""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.ashtakavarga.engine import (
    bindu_strength_label,
    compute_ashtakavarga,
)
from futurelens.ashtakavarga.tables import (
    BAV_TOTALS,
    CONTRIBUTORS,
    SAV_TOTAL,
    SUBJECTS,
    load_tables,
)
from futurelens.chart import cast_chart
from futurelens.models.ashtakavarga import (
    AshtakavargaReport,
    BAVResult,
    SAVResult,
)


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777


# --- Tables ---------------------------------------------------------------

def test_tables_load():
    tables = load_tables()
    assert set(tables.keys()) == set(SUBJECTS)


def test_tables_have_all_contributors():
    tables = load_tables()
    for subject in SUBJECTS:
        for contributor in CONTRIBUTORS:
            assert contributor in tables[subject]
            assert isinstance(tables[subject][contributor], list)
            assert len(tables[subject][contributor]) > 0


def test_bav_totals_sum_to_337():
    assert sum(BAV_TOTALS.values()) == SAV_TOTAL


# --- Engine ---------------------------------------------------------------

def test_compute_ashtakavarga_returns_report():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    assert isinstance(report, AshtakavargaReport)


def test_bav_for_all_subjects():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    assert set(report.bav.keys()) == set(SUBJECTS)


def test_bav_each_has_12_signs():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    for subject, bav in report.bav.items():
        assert len(bav.bindus_by_sign) == 12, subject


def test_bav_totals_match_classical():
    """The strong correctness check."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    for subject, bav in report.bav.items():
        assert bav.total == BAV_TOTALS[subject], (
            f"{subject}: got {bav.total}, expected {BAV_TOTALS[subject]}"
        )


def test_sav_total_is_337():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    assert report.sav.total == SAV_TOTAL


def test_sav_is_sum_of_bavs():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    for sign in range(12):
        expected = sum(
            bav.bindus_by_sign[sign] for bav in report.bav.values()
        )
        assert report.sav.bindus_by_sign[sign] == expected


# --- Helpers --------------------------------------------------------------

def test_bindu_for_sign():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    for sign in range(12):
        assert report.bindu_for_sign(sign) == report.sav.bindus_by_sign[sign]


def test_bindu_for_house():
    chart = cast_chart(BIRTH, LAT, LON)
    report = compute_ashtakavarga(chart)
    for house in range(1, 13):
        sign = chart.houses.house_signs[house]
        assert (
            report.bindu_for_house(chart.houses.house_signs, house)
            == report.sav.bindus_by_sign[sign]
        )


def test_bindu_strength_label():
    assert bindu_strength_label(30) == "VERY_STRONG"
    assert bindu_strength_label(25) == "STRONG"
    assert bindu_strength_label(20) == "MODERATE"
    assert bindu_strength_label(15) == "WEAK"
    assert bindu_strength_label(10) == "VERY_WEAK"


# --- Chart integration ----------------------------------------------------

def test_chart_ashtakavarga_method():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.ashtakavarga()
    assert isinstance(report, AshtakavargaReport)
    assert report.sav.total == SAV_TOTAL
