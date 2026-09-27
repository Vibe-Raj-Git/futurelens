"""
Chandra-Mangala Yoga.

BPHS ch. 36: Moon and Mars conjunct (or in mutual aspect in some
traditions). Wealth-producing yoga, but with emotional intensity.

Condition:
  Moon and Mars in the same sign (v0.2 uses conjunction only).
"""

from __future__ import annotations

from futurelens.grahas.relations import conjunct
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


def detect(chart) -> YogaResult:
    definition = YOGAS["CHANDRA_MANGALA"]
    met, failed = [], []

    if conjunct(chart, "MOON", "MARS"):
        met.append("moon_mars_conjunct")
    else:
        failed.append("moon_mars_conjunct")

    present = len(failed) == 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=("MOON", "MARS"),
        notes=(
            f"moon_sign={chart.grahas['MOON'].sign_index}",
            f"mars_sign={chart.grahas['MARS'].sign_index}",
        ),
    )
