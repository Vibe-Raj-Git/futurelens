from datetime import datetime

from futurelens.conventions import Conventions, UpagrahaEnumeration
from futurelens.models.chart import ChartContext
from futurelens.models.upagraha import UpagrahaName
from futurelens.upagraha.engine import UpagrahaEngine


def _context() -> ChartContext:
    return ChartContext(
        birth_datetime=datetime(2026, 1, 1, 12, 0, 0),
        latitude=28.61,
        longitude=77.20,
        ascendant_sign_index=0,
        house_signs={i + 1: (0 + i) % 12 for i in range(12)},
        house_lords={i + 1: "MARS" for i in range(12)},
        graha_longitudes={"SUN": 100.0},
        sunrise=datetime(2026, 1, 1, 6, 0, 0),
        sunset=datetime(2026, 1, 1, 18, 0, 0),
        ashtakavarga_bindus=None,
    )


def test_primary_nine_excludes_mrityu():
    engine = UpagrahaEngine(
        Conventions(upagraha_enumeration=UpagrahaEnumeration.PRIMARY_NINE)
    )
    report = engine.calculate(_context())
    assert UpagrahaName.MRITYU not in report.positions


def test_extended_kalavela_includes_mrityu():
    engine = UpagrahaEngine(
        Conventions(upagraha_enumeration=UpagrahaEnumeration.EXTENDED_KALAVELA)
    )
    report = engine.calculate(_context())
    assert UpagrahaName.MRITYU in report.positions


def test_ardhaprahara_dependency_flag_when_ashtakavarga_missing():
    engine = UpagrahaEngine(Conventions())
    report = engine.calculate(_context())
    assert "ASHTAKAVARGA" in report.dependencies
