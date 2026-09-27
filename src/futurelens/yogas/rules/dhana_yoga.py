"""
Dhana Yoga.

BPHS ch. 24: Combination between lords of the wealth houses
(2, 5, 9, 11). The classical definition allows conjunction,
mutual aspect, or exchange.

v0.2 condition:
  Any two wealth lords are conjunct, in mutual aspect, or in
  exchange with each other.
"""

from __future__ import annotations

from itertools import combinations

from futurelens.grahas.relations import conjunct, exchange, mutual_aspect
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


WEALTH_HOUSES = (2, 5, 9, 11)


def detect(chart) -> YogaResult:
    definition = YOGAS["DHANA_YOGA"]
    met, failed = [], []

    wealth_lords = {
        chart.houses.lord_of_house(h) for h in WEALTH_HOUSES
    }
    lord_list = sorted(wealth_lords)
    pairs = list(combinations(lord_list, 2))

    found = []
    for a, b in pairs:
        if conjunct(chart, a, b):
            found.append(f"{a}-{b}_conjunct")
        elif mutual_aspect(chart, a, b):
            found.append(f"{a}-{b}_mutual_aspect")
        elif exchange(chart, a, b):
            found.append(f"{a}-{b}_exchange")

    if found:
        met.extend(found)
    else:
        failed.append("no_relation_between_wealth_lords")

    present = len(failed) == 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=tuple(lord_list),
        involved_houses=WEALTH_HOUSES,
        notes=(
            f"wealth_lords={','.join(lord_list)}",
            f"relations_found={len(found)}",
        ),
    )
