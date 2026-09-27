"""
Convert Upagraha positions into typed evidence items.

Rules are intentionally minimal in v0.1. Each rule:
  - has a rule_id and classical basis
  - emits an Evidence object with provenance
  - never assigns a forecast score
"""

from __future__ import annotations

from futurelens.models.evidence import Direction, Evidence, EvidenceType
from futurelens.models.provenance import Provenance
from futurelens.models.upagraha import UpagrahaName, UpagrahaPosition
from futurelens.upagraha.definitions import DEFINITIONS


def _prov(rule_id: str, basis: str, method: str) -> Provenance:
    return Provenance(
        rule_id=rule_id,
        rule_version="0.1",
        tradition="PHALADEEPIKA",
        classical_basis=basis,
        calculation_method=method,
        calculation_convention="PHALADEEPIKA_25",
    )


def natal_placement_evidence(pos: UpagrahaPosition) -> Evidence:
    definition = DEFINITIONS[pos.name]
    direction = (
        Direction.PROTECTIVE
        if definition.role == "PROTECTIVE_MODIFIER"
        else Direction.ADVERSE
    )
    return Evidence(
        evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
        direction=direction,
        domain=None,
        upagraha=pos.name.value,
        target_evidence_id=None,
        classical_strength_ratio=definition.classical_strength_ratio,
        provenance=_prov(
            rule_id="UPG-NATAL-001",
            basis="Phaladeepika 25.19",
            method="natal_placement",
        ),
        notes=(
            f"house={pos.house}" if pos.house is not None else "house=UNKNOWN",
        ),
    )


def dasha_activation_evidence(
    pos: UpagrahaPosition,
    active_dasha_lord: str | None,
    house_lord: str | None,
) -> Evidence | None:
    """
    UPG-DASHA-001: effects manifest during the dasha of the lord of
    the house occupied by the Upagraha.

    Returns None if the activation rule does not apply.
    """
    if active_dasha_lord is None or house_lord is None:
        return None
    if active_dasha_lord != house_lord:
        return None
    definition = DEFINITIONS[pos.name]
    direction = (
        Direction.PROTECTIVE
        if definition.role == "PROTECTIVE_MODIFIER"
        else Direction.ADVERSE
    )
    return Evidence(
        evidence_type=EvidenceType.UPAGRAHA_DASHA_ACTIVATION,
        direction=direction,
        domain=None,
        upagraha=pos.name.value,
        target_evidence_id=None,
        classical_strength_ratio=definition.classical_strength_ratio,
        provenance=_prov(
            rule_id="UPG-DASHA-001",
            basis="Phaladeepika 25.25",
            method="house_lord_dasha_activation",
        ),
        notes=(f"active_dasha_lord={active_dasha_lord}",),
    )


def ardhaprahara_context_flag(
    pos: UpagrahaPosition,
    ashtakavarga_bindus: dict[int, int] | None,
) -> Evidence:
    """
    UPG-ARDHA-001. If Ashtakavarga is missing, emit CONTEXT_INCOMPLETE.
    """
    if pos.name != UpagrahaName.ARDHAPRAHARA:
        raise ValueError("ardhaprahara_context_flag only applies to ARDHAPRAHARA.")

    if ashtakavarga_bindus is None or pos.house is None:
        return Evidence(
            evidence_type=EvidenceType.UPAGRAHA_ASHTAKAVARGA_MODIFIER,
            direction=Direction.CONTEXT_INCOMPLETE,
            domain=None,
            upagraha=pos.name.value,
            target_evidence_id=None,
            classical_strength_ratio=DEFINITIONS[pos.name].classical_strength_ratio,
            provenance=_prov(
                rule_id="UPG-ARDHA-001",
                basis="Phaladeepika 25.21",
                method="ashtakavarga_bindus",
            ),
            notes=("Ashtakavarga missing; interpretation incomplete.",),
        )

    bindus = ashtakavarga_bindus.get(pos.house, 0)
    direction = Direction.PROTECTIVE if bindus >= 4 else Direction.ADVERSE
    return Evidence(
        evidence_type=EvidenceType.UPAGRAHA_ASHTAKAVARGA_MODIFIER,
        direction=direction,
        domain=None,
        upagraha=pos.name.value,
        target_evidence_id=None,
        classical_strength_ratio=DEFINITIONS[pos.name].classical_strength_ratio,
        provenance=_prov(
            rule_id="UPG-ARDHA-001",
            basis="Phaladeepika 25.21",
            method="ashtakavarga_bindus",
        ),
        notes=(f"bindus_in_house_{pos.house}={bindus}",),
    )
