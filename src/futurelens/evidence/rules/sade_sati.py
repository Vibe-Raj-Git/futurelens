"""
SAT-SADE-SATI-001: Saturn transiting the 12th, 1st, or 2nd nakshatra
from the natal Moon's nakshatra indicates Sade Sati.

The rule emits evidence on three phases:
  - Rising (12th from Moon nakshatra)
  - Peak    (same as Moon nakshatra)
  - Setting (2nd from Moon nakshatra)

Classical basis: derived from Gochara principles; the exact nakshatra
basis is used in most modern Jyotish software. The Rulebook records
this as the SAT-SADE-SATI convention.
"""

from __future__ import annotations

from futurelens.evidence.rules.base import EvidenceContext, make_provenance
from futurelens.models.evidence import Direction, Evidence, EvidenceType


class SadeSatiRule:
    """SAT-SADE-SATI-001."""

    rule_id = "SAT-SADE-SATI-001"
    rule_version = "0.1"
    tradition = "GOCHARA"
    classical_basis = "Gochara: Saturn transit from Moon nakshatra"
    calculation_method = "saturn_nakshatra_distance_from_moon"
    calculation_convention = "NAKSHATRA_BASED"

    def applies_to(self, ctx: EvidenceContext) -> bool:
        return True

    def emit(self, ctx: EvidenceContext) -> list[Evidence]:
        chart = ctx.chart
        natal_moon_nak = chart.grahas["MOON"].nakshatra.nakshatra_index

        transits = chart.transits_at(ctx.when)
        saturn = transits.positions["SATURN"]
        saturn_nak = saturn.graha.nakshatra.nakshatra_index

        distance = (saturn_nak - natal_moon_nak) % 27

        if distance == 26:
            phase = "RISING"
        elif distance == 0:
            phase = "PEAK"
        elif distance == 1:
            phase = "SETTING"
        else:
            return []

        return [Evidence(
            evidence_type=EvidenceType.UPAGRAHA_TRANSIT_TRIGGER,
            direction=Direction.ADVERSE,
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
                f"phase={phase}",
                f"saturn_nakshatra={saturn_nak}",
                f"moon_nakshatra={natal_moon_nak}",
                f"transit_sign={saturn.graha.sign_index}",
            ),
        )]
