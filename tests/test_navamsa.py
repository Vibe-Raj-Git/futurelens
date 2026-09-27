"""
Navamsa (D9) tests.

D9 is the first divisional chart. This test file covers:

  1. The transform itself, against the hand-verified reference table
     in rulebook/20_divisional_charts.yaml.
  2. D9 sign and D9 dignity per graha on the reference chart.
  3. The D1-vs-D9 reconciliation categories.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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


# Reference chart: 1984-08-30 12:02 IST, Ujjain (Scorpio lagna).
_IST = timezone(timedelta(hours=5, minutes=30))
_REFERENCE_BIRTH = (
    datetime(1984, 8, 30, 12, 2, 0, tzinfo=_IST)
    .astimezone(timezone.utc)
)
_REFERENCE_LAT = 22.7196
_REFERENCE_LON = 75.8577


def _reference_chart():
    return cast_chart(_REFERENCE_BIRTH, _REFERENCE_LAT, _REFERENCE_LON)


# =====================================================================
# 1. Transform
# =====================================================================

REFERENCE_TABLE = {
    0:  [0, 1, 2, 3, 4, 5, 6, 7, 8],
    1:  [9, 10, 11, 0, 1, 2, 3, 4, 5],
    2:  [6, 7, 8, 9, 10, 11, 0, 1, 2],
    3:  [3, 4, 5, 6, 7, 8, 9, 10, 11],
    4:  [0, 1, 2, 3, 4, 5, 6, 7, 8],
    5:  [9, 10, 11, 0, 1, 2, 3, 4, 5],
    6:  [6, 7, 8, 9, 10, 11, 0, 1, 2],
    7:  [3, 4, 5, 6, 7, 8, 9, 10, 11],
    8:  [0, 1, 2, 3, 4, 5, 6, 7, 8],
    9:  [9, 10, 11, 0, 1, 2, 3, 4, 5],
    10: [6, 7, 8, 9, 10, 11, 0, 1, 2],
    11: [3, 4, 5, 6, 7, 8, 9, 10, 11],
}


def test_navamsa_transform_matches_reference_table():
    from futurelens.vargas.navamsa import navamsa_sign_of

    for sign_index, expected in REFERENCE_TABLE.items():
        for navamsa_index, expected_d9 in enumerate(expected):
            # Mid-point of the navamsa slice, to avoid boundary
            # ambiguity.
            degree_in_sign = (
                navamsa_index * (30.0 / 9.0)
                + (30.0 / 18.0)
            )
            longitude = sign_index * 30.0 + degree_in_sign
            got = navamsa_sign_of(longitude)
            assert got == expected_d9, (
                f"sign={sign_index} navamsa={navamsa_index} "
                f"longitude={longitude:.4f} "
                f"expected={expected_d9} got={got}"
            )


# =====================================================================
# 2. D9 sign and dignity per graha on the reference chart
# =====================================================================

def test_d9_signs_reference_chart():
    from futurelens.vargas.navamsa import navamsa_of_chart

    chart = _reference_chart()
    d9 = navamsa_of_chart(chart)

    for name, pos in d9.positions.items():
        assert 0 <= pos.d9_sign_index <= 11, (
            f"{name} D9 sign out of range"
        )
        assert pos.d9_dignity in (
            "EXALTED", "MOOLATRIKONA", "OWN_SIGN",
            "DEBILITATED", "NEUTRAL",
        ), f"{name} D9 dignity unknown: {pos.d9_dignity}"


def test_d9_sign_of_known_longitude():
    """
    Verify the integration path: the D9 sign computed from a
    graha's D1 longitude on the reference chart matches the
    transform applied directly.
    """
    from futurelens.vargas.navamsa import navamsa_sign_of

    chart = _reference_chart()

    for name in ("JUPITER", "SUN", "MOON"):
        g = chart.grahas[name]
        sign_index = int(g.longitude // 30)
        degree_in_sign = g.longitude - sign_index * 30.0
        navamsa_index = int(degree_in_sign // (30.0 / 9.0))
        expected = (sign_index * 9 + navamsa_index) % 12
        assert navamsa_sign_of(g.longitude) == expected


# =====================================================================
# 3. Reconciliation
# =====================================================================

def test_reconciliation_produces_valid_category_per_graha():
    from futurelens.vargas.reconciliation import reconcile

    chart = _reference_chart()
    results = reconcile(chart)

    valid = {"CONFIRMED", "UPGRADED", "DOWNGRADED", "NEUTRAL"}
    for name, r in results.items():
        assert r.category in valid, (
            f"{name} has invalid reconciliation category: "
            f"{r.category}"
        )
        assert r.d1_dignity in (
            "EXALTED", "MOOLATRIKONA", "OWN_SIGN",
            "DEBILITATED", "NEUTRAL",
        )
        assert r.d9_dignity in (
            "EXALTED", "MOOLATRIKONA", "OWN_SIGN",
            "DEBILITATED", "NEUTRAL",
        )

# =====================================================================
# 4. Hard-assertion: exact D9 signs on the reference chart
# =====================================================================

REFERENCE_D9_SIGNS = {
    # name: (d1_sign, d1_deg, expected_d9_sign, expected_d9_dignity)
    # Hand-verified: (sign * 9 + floor(deg / 3.3333)) mod 12
    "SUN":     (4, 13.443404,  4, "MOOLATRIKONA"),
    "MOON":    (6,  2.219854,  6, "NEUTRAL"),
    "MARS":    (7, 13.307298,  6, "NEUTRAL"),
    "MERCURY": (4, 10.342033,  3, "NEUTRAL"),
    "JUPITER": (8,  9.506942,  2, "NEUTRAL"),
    "VENUS":   (5,  3.995467, 10, "NEUTRAL"),
    "SATURN":  (6, 17.888031, 11, "NEUTRAL"),
    "RAHU":    (1,  7.745254, 11, "NEUTRAL"),
    "KETU":    (7,  7.745254,  5, "NEUTRAL"),
}


def test_d9_signs_reference_chart_exact():
    """
    Hard-asserted D9 signs for every graha on the reference chart.

    The expected values are hand-computed from the D1 longitudes
    using the classical transform:

        d9_sign = (sign_index * 9 + floor(degree_in_sign / 3.3333)) mod 12

    If this test fails, either the transform is wrong or the D1
    longitudes have changed - both are real bugs.
    """
    from futurelens.vargas.navamsa import navamsa_of_chart

    chart = _reference_chart()
    d9 = navamsa_of_chart(chart)

    for name, (d1_sign, d1_deg, expected_sign, expected_dignity) in (
        REFERENCE_D9_SIGNS.items()
    ):
        g = chart.grahas[name]
        pos = d9.positions[name]

        assert g.sign_index == d1_sign, (
            f"{name}: D1 sign mismatch - expected {d1_sign}, "
            f"got {g.sign_index}"
        )
        assert abs(g.degree_in_sign - d1_deg) < 1e-3, (
            f"{name}: D1 degree mismatch - expected {d1_deg}, "
            f"got {g.degree_in_sign}"
        )
        assert pos.d9_sign_index == expected_sign, (
            f"{name}: D9 sign mismatch - expected {expected_sign}, "
            f"got {pos.d9_sign_index}"
        )
        assert pos.d9_dignity == expected_dignity, (
            f"{name}: D9 dignity mismatch - expected {expected_dignity}, "
            f"got {pos.d9_dignity}"
        )

REFERENCE_RECONCILIATION = {
    "SUN":     "CONFIRMED",
    "MOON":    "NEUTRAL",
    "MARS":    "NEUTRAL",
    "MERCURY": "NEUTRAL",
    "JUPITER": "NEUTRAL",
    "VENUS":   "NEUTRAL",
    "SATURN":  "NEUTRAL",
    "RAHU":    "NEUTRAL",
    "KETU":    "NEUTRAL",
}


def test_reconciliation_reference_chart_exact():
    """
    Hard-asserted reconciliation categories on the reference chart.

    Hand-derived from the D1 and D9 dignities above:

      SUN     : D1 strong (moolatrikona), D9 strong (moolatrikona)
                -> CONFIRMED
      MARS    : D1 strong (own sign in Scorpio), D9 neutral
                -> NEUTRAL
      JUPITER : D1 strong (own sign in Sagittarius), D9 neutral
                -> NEUTRAL
      all others: D1 neutral, D9 neutral -> NEUTRAL

    Note: this chart produces no UPGRADED or DOWNGRADED cases.
    A second reference chart (with a D1-strong / D9-weak graha)
    would test those categories; see future work.
    """
    from futurelens.vargas.reconciliation import reconcile

    chart = _reference_chart()
    results = reconcile(chart)

    for name, expected in REFERENCE_RECONCILIATION.items():
        got = results[name].category
        assert got == expected, (
            f"{name}: reconciliation mismatch - expected {expected}, "
            f"got {got} (d1={results[name].d1_dignity}, "
            f"d9={results[name].d9_dignity})"
        )