"""
Kemadruma Yoga.

Classical definition: the Moon has no graha in the 2nd or 12th
house from it (excluding the Sun, which is too close to count).

Result: isolation, loneliness, family estrangement, hardship
to the mother. It is one of the most significant adverse
yogas for family life.

Exceptions (Kemadruma Bhanga):
  - Moon conjunct or aspected by Jupiter, Venus, Mercury, or
    a strong waxing Moon's dispositor
  - Moon in kendra from Lagna with a benefic
  - Moon in own or exalted sign
"""

from __future__ import annotations

from futurelens.grahas.dignity import is_exalted, is_own_sign
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


BENEFICS = ("JUPITER", "VENUS", "MERCURY")


def detect(chart) -> YogaResult:
    definition = YOGAS["KEMADRUMA"]
    met, failed = [], []

    moon = chart.grahas["MOON"]
    moon_sign = moon.sign_index
    second_from_moon = (moon_sign + 1) % 12
    twelfth_from_moon = (moon_sign - 1) % 12

    # Check for occupants in 2nd or 12th from Moon.
    occupants_2 = []
    occupants_12 = []
    for name, pos in chart.grahas.items():
        if name in ("MOON", "SUN"):
            continue
        if pos.sign_index == second_from_moon:
            occupants_2.append(name)
        elif pos.sign_index == twelfth_from_moon:
            occupants_12.append(name)

    if occupants_2 or occupants_12:
        failed.append(
            f"occupied_2nd={occupants_2}_or_12th={occupants_12}"
        )
        return YogaResult(
            yoga_id=definition.id,
            yoga_name=definition.name,
            classical_basis=definition.classical_basis,
            present=False,
            conditions_met=(),
            conditions_failed=tuple(failed),
            involved_grahas=("MOON",),
            notes=(
                f"occupants_2nd_from_moon={occupants_2}",
                f"occupants_12th_from_moon={occupants_12}",
            ),
        )

    met.append("no_graha_in_2nd_or_12th_from_moon")

    # Cancellation conditions.
    cancelled = []
    for benefic in BENEFICS:
        b = chart.grahas[benefic]
        if b.sign_index == moon_sign:
            cancelled.append(f"{benefic}_conjunct_moon")

    if is_own_sign("MOON", moon_sign) or is_exalted("MOON", moon_sign):
        cancelled.append("moon_in_own_or_exalted_sign")

    present = len(cancelled) == 0

    if present:
        return YogaResult(
            yoga_id=definition.id,
            yoga_name=definition.name,
            classical_basis=definition.classical_basis,
            present=True,
            conditions_met=tuple(met),
            conditions_failed=(),
            involved_grahas=("MOON",),
            notes=(f"moon_sign={moon_sign}",),
        )

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=False,
        conditions_met=tuple(met),
        conditions_failed=tuple(f"cancelled_by_{c}" for c in cancelled),
        involved_grahas=("MOON",),
        notes=(f"moon_sign={moon_sign}",),
    )
