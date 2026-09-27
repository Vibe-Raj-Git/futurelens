"""Yoga detection tests."""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.models.yoga import YogaResult
from futurelens.yogas.detector import YogaReport, detect_yogas


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777


def test_detect_yogas_returns_report():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    assert isinstance(report, YogaReport)


def test_report_has_all_nine_yogas():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    ids = {r.yoga_id for r in report.results}
    expected = {
        "GAJA_KESARI",
        "CHANDRA_MANGALA",
        "DHANA_YOGA",
        "RAJA_YOGA",
        "LAKSHMI_YOGA",
        "PANCHA_MAHAPURUSHA",
        "NEECHA_BHANGA",
        "VIPARITA_RAJA",
        "KEMADRUMA",
    }
    assert ids == expected


def test_each_yoga_result_has_basis():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    for r in report.results:
        assert r.classical_basis != ""
        assert r.yoga_name != ""


def test_present_and_absent_partition():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    assert len(report.present) + len(report.absent) == len(report.results)


def test_summary_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    s = report.summary()
    assert s["total"] == 9
    assert s["present"] == len(report.present)
    assert isinstance(s["present_ids"], list)


def test_by_id_lookup():
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    gk = report.by_id("GAJA_KESARI")
    assert gk is not None
    assert gk.yoga_id == "GAJA_KESARI"


def test_chart_yogas_method():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.yogas()
    assert isinstance(report, YogaReport)


def test_gaja_kesari_condition_returns_bool():
    """Gaja Kesari is present or absent; either is valid."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    gk = report.by_id("GAJA_KESARI")
    assert isinstance(gk.present, bool)


def test_pancha_mahapurusha_partial_ok():
    """Pancha Mahapurusha may be partially formed; that is still present."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = detect_yogas(chart)
    pm = report.by_id("PANCHA_MAHAPURUSHA")
    assert isinstance(pm.present, bool)
    assert pm.classical_basis == "BPHS ch. 75"
