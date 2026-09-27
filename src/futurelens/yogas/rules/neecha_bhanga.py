"""
Neecha Bhanga Raja Yoga.

BPHS ch. 22: A debilitated planet's debilitation is cancelled if:
  - The lord of the debilitation sign is in a kendra from
    Lagna or Moon, OR
  - The lord of the exaltation sign is in a kendra from
    Lagna or Moon.

v0.2 condition:
  The chart contains at least one debilitated graha whose
  debilitation sign lord is in a kendra from Lagna or Moon.
"""

from __future__ import annotations

from futurelens.grahas.dignity import is_debilitated
from futurelens.grahas.relations import (
    graha_in_kendra_from_graha,
    is_kendra,
)
from futurelens.houses.resolver import SIGN_LORDS
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


GRAHAS_TO_CHECK = (
    "SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN",
)


def detect(chart) -> YogaResult:
    definition = YOGAS["NEECHA_BHANGA"]
    met, failed = [], []

    for name in GRAHAS_TO_CHECK:
        pos = chart.grahas[name]
        if not is_debilitated(name, pos.sign_index):
            continue

        debil_sign = pos.sign_index
        dispositor = SIGN_LORDS[debil_sign]
        dispositor_house_from_lagna = chart.grahas[dispositor].house

        # The dispositor must be in a kendra from Lagna or Moon.
        from_lagna = (
            dispositor_house_from_lagna is not None
            and is_kendra(dispositor_house_from_lagna)
        )
        from_moon = graha_in_kendra_from_graha(chart, dispositor, "MOON")

        if from_lagna or from_moon:
            met.append(f"{name}_debilitated_but_cancelled_by_{dispositor}")
        else:
            failed.append(f"{name}_debilitated_not_cancelled")

    present = len(met) > 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        notes=(f"cancellations={len(met)}",),
    )
