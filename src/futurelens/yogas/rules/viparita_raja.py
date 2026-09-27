"""
Viparita Raja Yoga.

Phaladeepika ch. 6: Lords of the dusthanas (6, 8, 12) placed in
one another's houses. The classical three forms:
  - Harsha: 6th lord in 8th or 12th
  - Sarala: 8th lord in 6th or 12th
  - Vimala: 12th lord in 6th or 8th

v0.2 condition:
  Any of the three specific placements above.
"""

from __future__ import annotations

from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


def detect(chart) -> YogaResult:
    definition = YOGAS["VIPARITA_RAJA"]
    met, failed = [], []

    sixth_lord = chart.houses.lord_of_house(6)
    eighth_lord = chart.houses.lord_of_house(8)
    twelfth_lord = chart.houses.lord_of_house(12)

    sixth_house = chart.grahas[sixth_lord].house
    eighth_house = chart.grahas[eighth_lord].house
    twelfth_house = chart.grahas[twelfth_lord].house

    # Harsha
    if sixth_house in (8, 12):
        met.append(f"Harsha_sixth_lord_{sixth_lord}_in_{sixth_house}")
    # Sarala
    if eighth_house in (6, 12):
        met.append(f"Sarala_eighth_lord_{eighth_lord}_in_{eighth_house}")
    # Vimala
    if twelfth_house in (6, 8):
        met.append(f"Vimala_twelfth_lord_{twelfth_lord}_in_{twelfth_house}")

    present = len(met) > 0
    if not present:
        failed.append("no_viparita_placement")

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=(sixth_lord, eighth_lord, twelfth_lord),
        involved_houses=(6, 8, 12),
        notes=(
            f"sixth_lord={sixth_lord}_in_house_{sixth_house}",
            f"eighth_lord={eighth_lord}_in_house_{eighth_house}",
            f"twelfth_lord={twelfth_lord}_in_house_{twelfth_house}",
        ),
    )
