from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from futurelens.models.provenance import Provenance


class EvidenceType(str, Enum):
    """
    Broad category of the evidence.

    Used for grouping and filtering, not for interpretation.
    Rules should prefer to set subject / finding / interpretation
    explicitly rather than relying on the type.
    """
    UPAGRAHA_NATAL_PLACEMENT = "UPAGRAHA_NATAL_PLACEMENT"
    UPAGRAHA_HOUSE_ASSOCIATION = "UPAGRAHA_HOUSE_ASSOCIATION"
    UPAGRAHA_LORD_ASSOCIATION = "UPAGRAHA_LORD_ASSOCIATION"
    UPAGRAHA_PLANET_ASSOCIATION = "UPAGRAHA_PLANET_ASSOCIATION"
    UPAGRAHA_DASHA_ACTIVATION = "UPAGRAHA_DASHA_ACTIVATION"
    UPAGRAHA_TRANSIT_TRIGGER = "UPAGRAHA_TRANSIT_TRIGGER"
    UPAGRAHA_ASHTAKAVARGA_MODIFIER = "UPAGRAHA_ASHTAKAVARGA_MODIFIER"
    UPAGRAHA_PROTECTIVE_MODIFIER = "UPAGRAHA_PROTECTIVE_MODIFIER"
    UPAGRAHA_ADVERSE_MODIFIER = "UPAGRAHA_ADVERSE_MODIFIER"
    FAMILY_RELATIONSHIP = "FAMILY_RELATIONSHIP"


class Direction(str, Enum):
    ADVERSE = "ADVERSE"
    PROTECTIVE = "PROTECTIVE"
    CONTEXT_INCOMPLETE = "CONTEXT_INCOMPLETE"


class Weight(str, Enum):
    """
    Astrological importance tier.

    STRUCTURAL - the fundamental promise of the chart. Lordships,
        yogas, own-sign placements, Lagna strength. This is what
        the reading leads with.

    SUPPORTING - secondary indicators that reinforce or qualify the
        structural picture. Dasha activation, benign placements in
        favourable houses.

    MODIFIER   - adjusts at the margins. Combustion, Upagrahas,
        transits, debilitation. Cannot override structural evidence.

    Volume does not equal importance. One STRUCTURAL item outweighs
    many MODIFIERs.
    """
    STRUCTURAL = "STRUCTURAL"
    SUPPORTING = "SUPPORTING"
    MODIFIER = "MODIFIER"
    STRONG_MODIFIER = "STRONG_MODIFIER"


@dataclass(frozen=True)
class Evidence:
    """
    A single piece of astrological evidence.

    Semantic fields
    ---------------
    subject         What the evidence is about, in a short phrase.
                    Examples: "2nd house lord Jupiter",
                              "Mother relationship",
                              "Jupiter as significator",
                              "Jupiter transit"
    finding         The plain-English fact the rule has determined.
                    Examples: "Jupiter is in its own sign in the 2nd house.",
                              "Saturn is in the 12th house, a dusthana."
    interpretation  Why the fact matters for the domain.
                    Examples: "This is a strong placement for family lineage.",
                              "This weakens the significations of the mother."

    These three fields are populated at emission time by each rule.
    Downstream consumers (the API, the LLM payload, the template
    backend) read them directly. No downstream consumer should parse
    the notes field.

    notes           The structured key=value raw data. Kept for
                    debugging, audit, and external tools. Never sent
                    to the LLM once Phase 4 is complete.
    """

    evidence_type: EvidenceType
    direction: Direction
    domain: Optional[str]
    upagraha: Optional[str]
    target_evidence_id: Optional[str]
    classical_strength_ratio: float
    provenance: Provenance
    weight: Weight = Weight.MODIFIER

    subject: str = ""
    finding: str = ""
    interpretation: str = ""

    notes: tuple[str, ...] = field(default_factory=tuple)

    def is_valid(self) -> bool:
        if self.evidence_type == EvidenceType.UPAGRAHA_PROTECTIVE_MODIFIER:
            return self.target_evidence_id is not None
        return True

    def is_semantic(self) -> bool:
        """True if the rule populated the semantic fields."""
        return bool(self.subject or self.finding or self.interpretation)
