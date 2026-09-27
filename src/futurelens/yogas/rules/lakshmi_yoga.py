"""
Lakshmi Yoga.

Phaladeepika ch. 6: The lord of the 9th is in own, exalted, or
moolatrikona sign, the Lagna lord is strong, and Jupiter or Venus
is in a kendra.

v0.2 condition:
  - 9th lord is exalted, moolatrikona, or own sign
  - Jupiter or Venus in a kendra (1, 4, 7, 10) from Lagna
"""

from __future__ import annotations

from futurelens.grahas.dignity import is_strong_in_sign
from futurelens.grahas.relations import is_kendra
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


def detect(chart) -> YogaResult:
    definition = YOGAS["LAKSHMI_YOGA"]
    met, failed = [], []

    # Condition 1: 9th lord strong
    ninth_lord = chart.houses.lord_of_house(9)
    ninth_pos = chart.grahas[ninth_lord]
    if is_strong_in_sign(ninth_lord, ninth_pos.sign_index):
        met.append(f"ninth_lord_{ninth_lord}_is_strong")
    else:
        failed.append(f"ninth_lord_{ninth_lord}_is_not_strong")

    # Condition 2: Jupiter or Venus in kendra
    jup_house = chart.grahas["JUPITER"].house
    ven_house = chart.grahas["VENUS"].house
    jup_kendra = jup_house is not None and is_kendra(jup_house)
    ven_kendra = ven_house is not None and is_kendra(ven_house)

    if jup_kendra or ven_kendra:
        met.append("jupiter_or_venus_in_kendra")
    else:
        failed.append("jupiter_or_venus_not_in_kendra")

    present = len(failed) == 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=(ninth_lord, "JUPITER", "VENUS"),
        involved_houses=(9,),
        notes=(
            f"ninth_lord={ninth_lord}",
            f"jupiter_house={jup_house}",
            f"venus_house={ven_house}",
        ),
    )
