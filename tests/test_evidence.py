from datetime import datetime

from futurelens.models.evidence import Direction, EvidenceType
from futurelens.models.upagraha import (
    UpagrahaFamily,
    UpagrahaName,
    UpagrahaPosition,
)
from futurelens.upagraha.evidence_rules import (
    ardhaprahara_context_flag,
    natal_placement_evidence,
)


def test_natal_placement_evidence_has_provenance():
    pos = UpagrahaPosition(
        name=UpagrahaName.GULIKA,
        family=UpagrahaFamily.KALAVELA,
        longitude=45.0,
        sign_index=1,
        degree_in_sign=15.0,
        house=8,
    )
    ev = natal_placement_evidence(pos)
    assert ev.provenance.rule_id
    assert ev.provenance.tradition == "PHALADEEPIKA"
    assert ev.direction == Direction.ADVERSE


def test_ardhaprahara_context_incomplete_without_ashtakavarga():
    pos = UpagrahaPosition(
        name=UpagrahaName.ARDHAPRAHARA,
        family=UpagrahaFamily.KALAVELA,
        longitude=10.0,
        sign_index=0,
        degree_in_sign=10.0,
        house=3,
    )
    ev = ardhaprahara_context_flag(pos, ashtakavarga_bindus=None)
    assert ev.direction == Direction.CONTEXT_INCOMPLETE
    assert ev.evidence_type == EvidenceType.UPAGRAHA_ASHTAKAVARGA_MODIFIER
