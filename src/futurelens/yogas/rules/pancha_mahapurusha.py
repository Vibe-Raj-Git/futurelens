"""
Pancha Mahapurusha Yoga.

BPHS ch. 75: Mars, Mercury, Jupiter, Venus, or Saturn in own,
exalted, or moolatrikona sign, AND in a kendra (1, 4, 7, 10)
from Lagna.

Produces five distinct yogas:
  Ruchaka (Mars), Bhadra (Mercury), Hamsa (Jupiter),
  Malavya (Venus), Sasa (Saturn).
"""

from __future__ import annotations

from futurelens.grahas.dignity import is_strong_in_sign
from futurelens.grahas.relations import is_kendra
from futurelens.models.yoga import YogaResult
from futurelens.yogas.definitions import YOGAS


GRAHAS_TO_CHECK = ("MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")

SPECIFIC_NAMES = {
    "MARS": "Ruchaka",
    "MERCURY": "Bhadra",
    "JUPITER": "Hamsa",
    "VENUS": "Malavya",
    "SATURN": "Sasa",
}


def detect(chart) -> YogaResult:
    definition = YOGAS["PANCHA_MAHAPURUSHA"]
    met, failed = [], []

    for name in GRAHAS_TO_CHECK:
        pos = chart.grahas[name]
        if pos.house is None:
            failed.append(f"{name}_house_unknown")
            continue
        strong = is_strong_in_sign(name, pos.sign_index)
        kendra = is_kendra(pos.house)
        if strong and kendra:
            met.append(
                f"{SPECIFIC_NAMES[name]}({name})_strong_in_kendra"
            )
        else:
            reasons = []
            if not strong:
                reasons.append("not_strong_in_sign")
            if not kendra:
                reasons.append("not_in_kendra")
            failed.append(f"{name}_{'+'.join(reasons)}")

    # Present if at least one of the five is formed.
    present = len(met) > 0

    return YogaResult(
        yoga_id=definition.id,
        yoga_name=definition.name,
        classical_basis=definition.classical_basis,
        present=present,
        conditions_met=tuple(met),
        conditions_failed=tuple(failed),
        involved_grahas=GRAHAS_TO_CHECK,
        involved_houses=(1, 4, 7, 10),
        notes=(f"formed_count={len(met)}",),
    )
