"""
Vimshottari Dasha engine.

Computes Mahadasha, Antardasha, and Pratyantardasha sequences from
the Moon's nakshatra position at birth.

The Moon's nakshatra lord at birth determines the FIRST Mahadasha.
The proportion of that nakshatra remaining at birth determines the
BALANCE of the first Mahadasha.

All durations are relative to the birth moment (t=0).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from futurelens.dasha.definitions import (
    DAYS_PER_YEAR,
    DASHA_LORDS,
    DASHA_YEARS,
    NAKSHATRA_TO_DASHA_LORD,
    DashaPeriod,
    next_lord,
)
from futurelens.grahas.nakshatra import NAKSHATRA_SIZE_DEG


def _proportional_periods(
    parent_lord: str,
    parent_duration_days: float,
    parent_start_days: float,
    level: str,
) -> list[DashaPeriod]:
    """
    Compute sub-periods inside a parent period.

    Sub-periods start from the parent lord and proceed in Vimshottari
    order. Each sub-period's duration is proportional to the sub-lord's
    Mahadasha years.
    """
    # The sub-period sequence starts from the parent lord and cycles
    # through all nine.
    start_idx = DASHA_LORDS.index(parent_lord)
    total_years = sum(DASHA_YEARS.values())  # 120

    periods: list[DashaPeriod] = []
    cursor = parent_start_days

    for offset in range(9):
        sub_lord = DASHA_LORDS[(start_idx + offset) % 9]
        share = DASHA_YEARS[sub_lord] / total_years
        duration = parent_duration_days * share
        periods.append(DashaPeriod(
            lord=sub_lord,
            start_days=cursor,
            end_days=cursor + duration,
            level=level,
            parent_lord=parent_lord,
        ))
        cursor += duration

    return periods


def compute_mahadashas(
    moon_longitude: float,
    birth_datetime: datetime,
) -> list[DashaPeriod]:
    """
    Compute the Mahadasha sequence starting at birth.

    The first Mahadasha's duration is the balance (remaining portion)
    at the moment of birth. Subsequent Mahadashas are full length.
    """
    # Determine the nakshatra index (0..26) and position within it.
    nakshatra_index = int(moon_longitude // NAKSHATRA_SIZE_DEG)
    nakshatra_index = min(nakshatra_index, 26)

    position_in_nakshatra = moon_longitude - (nakshatra_index * NAKSHATRA_SIZE_DEG)
    fraction_elapsed = position_in_nakshatra / NAKSHATRA_SIZE_DEG
    fraction_remaining = 1.0 - fraction_elapsed

    first_lord = NAKSHATRA_TO_DASHA_LORD[nakshatra_index]
    first_lord_years = DASHA_YEARS[first_lord]
    first_lord_days_full = first_lord_years * DAYS_PER_YEAR
    first_lord_days_balance = first_lord_days_full * fraction_remaining

    periods: list[DashaPeriod] = []

    # First Mahadasha is partial.
    periods.append(DashaPeriod(
        lord=first_lord,
        start_days=0.0,
        end_days=first_lord_days_balance,
        level="MAHADASHA",
    ))

    # Subsequent Mahadashas are full length, in sequence.
    cursor = first_lord_days_balance
    current = first_lord
    for _ in range(8):
        current = next_lord(current)
        duration = DASHA_YEARS[current] * DAYS_PER_YEAR
        periods.append(DashaPeriod(
            lord=current,
            start_days=cursor,
            end_days=cursor + duration,
            level="MAHADASHA",
        ))
        cursor += duration

    return periods


def compute_antardashas(mahadasha: DashaPeriod) -> list[DashaPeriod]:
    """Sub-periods of a Mahadasha."""
    return _proportional_periods(
        parent_lord=mahadasha.lord,
        parent_duration_days=mahadasha.end_days - mahadasha.start_days,
        parent_start_days=mahadasha.start_days,
        level="ANTARDASHA",
    )


def compute_pratyantardashas(antardasha: DashaPeriod) -> list[DashaPeriod]:
    """Sub-periods of an Antardasha."""
    return _proportional_periods(
        parent_lord=antardasha.lord,
        parent_duration_days=antardasha.end_days - antardasha.start_days,
        parent_start_days=antardasha.start_days,
        level="PRATYANTARDASHA",
    )


def active_period(
    periods: list[DashaPeriod],
    at_days: float,
) -> DashaPeriod | None:
    """Return the period containing at_days, or None if outside range."""
    for p in periods:
        if p.start_days <= at_days < p.end_days:
            return p
    return None


def dasha_timeline(
    moon_longitude: float,
    birth_datetime: datetime,
) -> dict:
    """
    Full dasha timeline: Mahadashas, with Antardashas nested.

    Returns a dict with:
      birth_datetime
      mahadashas        -- list of DashaPeriod
      antardashas       -- {mahadasha_index: [DashaPeriod, ...]}
    """
    mahadashas = compute_mahadashas(moon_longitude, birth_datetime)
    antardashas = {i: compute_antardashas(m) for i, m in enumerate(mahadashas)}
    return {
        "birth_datetime": birth_datetime,
        "mahadashas": mahadashas,
        "antardashas": antardashas,
    }
