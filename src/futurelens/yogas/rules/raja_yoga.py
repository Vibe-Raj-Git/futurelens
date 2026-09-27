"""
Raja Yoga.

BPHS ch. 39: Combination between a kendra lord and a trikona lord.
This is the primary yoga of power, status, and authority.

v0.2 condition:
  A lord of a kendra (1, 4, 7, 10) is conjunct, in mutual aspect,
  or in exchange with a lord of a trikona (1, 5, 9).
"""

from __future__ import annotations

from futurelens.grahas.relations import conjunct, exchange, mutual_aspect
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


KENDRAS = (1, 4, 7, 10)
TRIKONAS = (1, 5, 9)


def detect(chart) -> YogaResult:
    definition = YOGAS["RAJA_YOGA"]
    met, failed = [], []

    kendra_lords = {chart.houses.lord_of_house(h) for h in KENDRAS}
    trikona_lords = {chart.houses.lord_of_house(h) for h in TRIKONAS}

    found = []
    for k in kendra_lords:
        for t in trikona_lords:
            if k == t:
                continue
            if conjunct(chart, k, t):
                found.append(f"kendra_{k}-trikona_{t}_conjunct")
            elif mutual_aspect(chart, k, t):
                found.append(f"kendra_{k}-trikona_{t}_mutual_aspect")
            elif exchange(chart, k, t):
                found.append(f"kendra_{k}-trikona_{t}_exchange")

    if found:
        met.extend(found)
    else:
        failed.append("no_relation_between_kendra_and_trikona_lords")

    present = len(failed) == 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=tuple(sorted(kendra_lords | trikona_lords)),
        involved_houses=KENDRAS + TRIKONAS,
        notes=(f"relations_found={len(found)}",),
    )
