"""
Ashtakavarga engine.

Computes Bhinnashtakavarga (BAV) for each of the seven planets and
Sarvastakavarga (SAV) as the sum.

Method (BPHS ch. 66):
  For each subject planet S (SUN through SATURN), and each
  contributor C (the seven planets plus LAGNA), the classical
  tables specify a set of houses counted from C. For each such
  house H:
     - Find the sign that is H houses from C's sign.
     - Add a bindu to that sign in S's BAV.

The LAGNA contributor uses the chart's ascendant sign.

The SAV is the sum of the seven BAVs, sign by sign.

Classical totals:
  SUN 48, MOON 49, MARS 39, MERCURY 54, JUPITER 56,
  VENUS 52, SATURN 39. Total SAV = 337.
"""

from __future__ import annotations

from futurelens.ashtakavarga.tables import (
    BAV_TOTALS,
    CONTRIBUTORS,
    SAV_TOTAL,
    SUBJECTS,
    load_tables,
)
from futurelens.models.ashtakavarga import (
    AshtakavargaReport,
    BAVResult,
    SAVResult,
)


def _sign_of(chart, contributor: str) -> int:
    """Sign index of a contributor. LAGNA uses the ascendant."""
    if contributor == "LAGNA":
        return chart.ascendant.sign_index
    return chart.grahas[contributor].sign_index


def _compute_bav(
    chart,
    subject: str,
    tables: dict[str, dict[str, list[int]]],
) -> BAVResult:
    """Compute Bhinnashtakavarga for one subject planet."""
    bindus = [0] * 12

    subject_table = tables[subject]
    for contributor in CONTRIBUTORS:
        contributor_sign = _sign_of(chart, contributor)
        offsets = subject_table[contributor]
        for offset in offsets:
            # House counted from contributor: sign = contributor_sign + (offset - 1)
            target_sign = (contributor_sign + offset - 1) % 12
            bindus[target_sign] += 1

    return BAVResult(
        subject=subject,
        bindus_by_sign=tuple(bindus),
        total=sum(bindus),
    )


def compute_ashtakavarga(chart) -> AshtakavargaReport:
    """
    Compute BAV for all seven subjects and the SAV.

    Raises RuntimeError if the computed totals do not match the
    classical constants. This is a strong correctness check.
    """
    tables = load_tables()

    bav_results: dict[str, BAVResult] = {}
    for subject in SUBJECTS:
        bav_results[subject] = _compute_bav(chart, subject, tables)

    # Verify classical BAV totals.
    for subject, result in bav_results.items():
        expected = BAV_TOTALS[subject]
        if result.total != expected:
            raise RuntimeError(
                f"BAV total mismatch for {subject}: "
                f"computed {result.total}, expected {expected}. "
                f"This indicates a bug in the bindu tables or "
                f"the computation."
            )

    # Compute SAV.
    sav_bindus = [0] * 12
    for result in bav_results.values():
        for i, count in enumerate(result.bindus_by_sign):
            sav_bindus[i] += count

    sav = SAVResult(
        bindus_by_sign=tuple(sav_bindus),
        total=sum(sav_bindus),
    )

    if sav.total != SAV_TOTAL:
        raise RuntimeError(
            f"SAV total mismatch: computed {sav.total}, "
            f"expected {SAV_TOTAL}."
        )

    return AshtakavargaReport(bav=bav_results, sav=sav)


def bindu_strength_label(bindus: int) -> str:
    """
    Classify an SAV bindu count into a strength label.

    Common convention:
      >= 30: very strong
      25-29: strong
      20-24: moderate
      15-19: weak
      < 15:  very weak

    The average across 12 signs is 337/12 = 28.08, so 28 is
    "average". The thresholds below are widely used.
    """
    if bindus >= 30:
        return "VERY_STRONG"
    if bindus >= 25:
        return "STRONG"
    if bindus >= 20:
        return "MODERATE"
    if bindus >= 15:
        return "WEAK"
    return "VERY_WEAK"
