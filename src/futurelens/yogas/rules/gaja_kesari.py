"""
Gaja Kesari Yoga.

BPHS ch. 36: Jupiter in a kendra (1, 4, 7, 10) from the Moon.

Condition:
  Jupiter in kendra from Moon.

Result: a benefic yoga indicating wisdom, respect, and support.
"""

from __future__ import annotations

from futurelens.grahas.relations import graha_in_kendra_from_graha
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


def detect(chart) -> YogaResult:
    definition = YOGAS["GAJA_KESARI"]
    met, failed = [], []

    jup_kendra_from_moon = graha_in_kendra_from_graha(chart, "JUPITER", "MOON")
    if jup_kendra_from_moon:
        met.append("jupiter_in_kendra_from_moon")
    else:
        failed.append("jupiter_in_kendra_from_moon")

    present = len(failed) == 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=("JUPITER", "MOON"),
        notes=(
            f"jupiter_sign={chart.grahas['JUPITER'].sign_index}",
            f"moon_sign={chart.grahas['MOON'].sign_index}",
        ),
    )
