"""
UPG-DASHA-001: Upagraha effects manifest during the dasha of the
lord of the house occupied by the Upagraha.

Classical basis: Phaladeepika 25.25.

The rule triggers when:
  - an Upagraha is placed in some house of the natal chart
  - the lord of that house is the currently active Mahadasha or
    Antardasha lord

The rule emits evidence tagged with the Upagraha, its house, the
active dasha lord, and the direction (adverse for most, protective
for Yamakantaka).
"""

from __future__ import annotations

from futurelens.evidence.rules.base import EvidenceContext, make_provenance
from futurelens.models.evidence import Direction, Evidence, EvidenceType
from futurelens.models.upagraha import UpagrahaName
from futurelens.upagraha.definitions import DEFINITIONS


class UpagrahaDashaRule:
    """UPG-DASHA-001."""

    rule_id = "UPG-DASHA-001"
    rule_version = "0.1"
    tradition = "PHALADEEPIKA"
    classical_basis = "Phaladeepika 25.25"
    calculation_method = "house_lord_dasha_activation"
    calculation_convention = "PHALADEEPIKA_25"

    def applies_to(self, ctx: EvidenceContext) -> bool:
        return True

    def emit(self, ctx: EvidenceContext) -> list[Evidence]:
        chart = ctx.chart
        dasha = chart.dasha_at(ctx.when)

        active_lords = {dasha.mahadasha_lord, dasha.antardasha_lord}

        evidence: list[Evidence] = []

        for name, pos in chart.upagrahas.positions.items():
            if pos.house is None:
                continue
            house_lord = chart.houses.lord_of_house(pos.house)
            if house_lord not in active_lords:
                continue

            definition = DEFINITIONS.get(name)
            if definition is None:
                continue

            direction = (
                Direction.PROTECTIVE
                if definition.role == "PROTECTIVE_MODIFIER"
                else Direction.ADVERSE
            )

            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_DASHA_ACTIVATION,
                direction=direction,
                domain=None,
                upagraha=name.value,
                target_evidence_id=None,
                classical_strength_ratio=definition.classical_strength_ratio,
                provenance=make_provenance(
                    rule_id=self.rule_id,
                    classical_basis=self.classical_basis,
                    calculation_method=self.calculation_method,
                    calculation_convention=self.calculation_convention,
                    rule_version=self.rule_version,
                    tradition=self.tradition,
                ),
                notes=(
                    f"house={pos.house}",
                    f"house_lord={house_lord}",
                    f"mahadasha={dasha.mahadasha_lord}",
                    f"antardasha={dasha.antardasha_lord}",
                ),
            ))

        return evidence
