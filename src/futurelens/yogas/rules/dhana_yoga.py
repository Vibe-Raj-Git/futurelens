"""
Dhana Yoga.

BPHS ch. 24 and Phaladeepika: combinations between the lords of the
wealth houses (2, 5, 9, 11), or one graha that rules two or more of
them.

v0.4 conditions (any one qualifies):
  - two distinct wealth lords are conjunct, in mutual aspect, or in
    exchange                              (BPHS ch. 24 core)
  - one graha rules two or more wealth houses  (shared lordship)
  - a wealth lord occupies another wealth house
  - a wealth lord occupies its own sign in a wealth house

Disqualifiers do not suppress the yoga. They are reported as
additional entries in conditions_met with a weakened_by_ prefix,
so the LLM can preserve the tension rather than average it away.
"""

from __future__ import annotations

from itertools import combinations

from futurelens.grahas.dignity import is_debilitated, is_own_sign
from futurelens.grahas.relations import conjunct, exchange, mutual_aspect
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


WEALTH_HOUSES = (2, 5, 9, 11)

# Dusthanas per BPHS: 6, 8, 12.
_DUSTHANAS = (6, 8, 12)


def _lord_of_each_wealth_house(chart) -> dict[int, str]:
    return {h: chart.houses.lord_of_house(h) for h in WEALTH_HOUSES}


def _houses_ruled_by(chart, graha: str) -> list[int]:
    """Which of the wealth houses does this graha rule?"""
    return [
        h for h in WEALTH_HOUSES
        if chart.houses.lord_of_house(h) == graha
    ]


def _is_in_dusthana(chart, graha: str) -> bool:
    house = chart.grahas[graha].house
    return house is not None and house in _DUSTHANAS


def detect(chart) -> YogaResult:
    definition = YOGAS["DHANA_YOGA"]

    met: list[str] = []
    failed: list[str] = []

    lord_of_house = _lord_of_each_wealth_house(chart)
    distinct_lords = sorted(set(lord_of_house.values()))

    # ---------------------------------------------------------------
    # Condition 1 — two distinct wealth lords in relationship.
    # ---------------------------------------------------------------
    relation_found = False
    for a, b in combinations(distinct_lords, 2):
        if conjunct(chart, a, b):
            met.append(f"{a}-{b}_conjunct")
            relation_found = True
        elif mutual_aspect(chart, a, b):
            met.append(f"{a}-{b}_mutual_aspect")
            relation_found = True
        elif exchange(chart, a, b):
            met.append(f"{a}-{b}_exchange")
            relation_found = True

    if not relation_found:
        failed.append("no_relation_between_wealth_lords")

    # ---------------------------------------------------------------
    # Condition 2 — shared lordship: one graha rules >= 2 wealth houses.
    # ---------------------------------------------------------------
    shared_lordship_found = False
    for graha in distinct_lords:
        ruled = _houses_ruled_by(chart, graha)
        if len(ruled) >= 2:
            key = "_".join(str(h) for h in sorted(ruled))
            met.append(f"shared_lordship_{key}={graha}")
            shared_lordship_found = True

    if not shared_lordship_found:
        failed.append("no_shared_lordship_of_wealth_houses")

    # ---------------------------------------------------------------
    # Condition 3 — a wealth lord occupies a wealth house.
    # ---------------------------------------------------------------
    occupies_found = False
    for graha in distinct_lords:
        house = chart.grahas[graha].house
        if house is not None and house in WEALTH_HOUSES:
            met.append(f"occupies_wealth_house={graha}")
            occupies_found = True

    if not occupies_found:
        failed.append("no_wealth_lord_in_a_wealth_house")

    # ---------------------------------------------------------------
    # Condition 4 — a wealth lord in its own sign in a wealth house.
    # ---------------------------------------------------------------
    own_sign_found = False
    for graha in distinct_lords:
        g = chart.grahas[graha]
        house = g.house
        if house is None or house not in WEALTH_HOUSES:
            continue
        if is_own_sign(graha, g.sign_index):
            met.append(f"own_sign_in_wealth_house={graha}")
            own_sign_found = True

    if not own_sign_found:
        failed.append("no_wealth_lord_in_own_sign_in_wealth_house")

    # ---------------------------------------------------------------
    # Disqualifier flags — annotate, do not suppress.
    # ---------------------------------------------------------------
    for graha in distinct_lords:
        g = chart.grahas[graha]
        if g.combust:
            met.append(f"weakened_by_combustion={graha}")
        if is_debilitated(graha, g.sign_index):
            met.append(f"weakened_by_debilitation={graha}")
        if _is_in_dusthana(chart, graha):
            met.append(f"weakened_by_dusthana={graha}")

    # ---------------------------------------------------------------
    # Presence: any core structural condition qualifies.
    # Disqualifier flags are never the sole reason for presence.
    # ---------------------------------------------------------------
    present = (
        relation_found
        or shared_lordship_found
        or occupies_found
        or own_sign_found
    )

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=(
            "BPHS ch. 24; Phaladeepika ch. 6 (wealth combinations)"
        ),
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=tuple(distinct_lords),
        involved_houses=WEALTH_HOUSES,
        notes=(
            f"wealth_lords={','.join(distinct_lords)}",
            f"relations_found={relation_found}",
            f"shared_lordship={shared_lordship_found}",
            f"occupies_wealth_house={occupies_found}",
            f"own_sign_in_wealth_house={own_sign_found}",
        ),
    )