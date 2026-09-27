"""
NATAL-PLACEMENT-001: A graha occupying a house produces evidence about
that house's significations.

This is a base rule. It does not interpret; it only says "graha X is
in house Y". Domain engines extend this by adding domain-specific
interpretation.

The rule emits one evidence item per natal graha placement, tagged
with the graha, the house, and the sign. Direction is NATIVE (neither
adverse nor protective) because the classical texts do not assign a
universal direction to a graha in a house - that depends on the
graha's functional role for the specific ascendant.
"""

from __future__ import annotations

from futurelens.evidence.rules.base import EvidenceContext, make_provenance
from futurelens.models.evidence import Direction, Evidence, EvidenceType


class NatalPlacementRule:
    """NATAL-PLACEMENT-001."""

    rule_id = "NATAL-PLACEMENT-001"
    rule_version = "0.1"
    tradition = "PHALADEEPIKA"
    classical_basis = "General graha placement in houses"
    calculation_method = "natal_graha_house"
    calculation_convention = "WHOLE_SIGN"

    def applies_to(self, ctx: EvidenceContext) -> bool:
        return True

    def emit(self, ctx: EvidenceContext) -> list[Evidence]:
        chart = ctx.chart
        evidence: list[Evidence] = []

        for name, pos in chart.grahas.items():
            if pos.house is None:
                continue

            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
                direction=Direction.ADVERSE,  # placeholder; domain engines refine
                domain=None,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                provenance=make_provenance(
                    rule_id=self.rule_id,
                    classical_basis=self.classical_basis,
                    calculation_method=self.calculation_method,
                    calculation_convention=self.calculation_convention,
                    rule_version=self.rule_version,
                    tradition=self.tradition,
                ),
                notes=(
                    f"graha={name}",
                    f"house={pos.house}",
                    f"sign={pos.sign_index}",
                    f"retrograde={pos.retrograde}",
                    f"combust={pos.combust}",
                    f"nakshatra={pos.nakshatra.nakshatra_name}",
                ),
            ))

        return evidence
