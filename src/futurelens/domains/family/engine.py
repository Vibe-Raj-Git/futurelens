"""
FAMILY domain engine.

Runs the family evidence rules against a chart and returns a
structured FamilyReport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from futurelens.domains.family import rules as family_rules
from futurelens.evidence.graph import Contradiction, _detect_contradictions
from futurelens.models.evidence import Direction, Evidence


@dataclass
class FamilyReport:
    """The family-domain evidence for a chart at a given moment."""

    when: datetime
    evidence: list[Evidence] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    rules_evaluated: list[str] = field(default_factory=list)
    rules_failed: list[str] = field(default_factory=list)

    def by_rule(self, rule_id: str) -> list[Evidence]:
        return [e for e in self.evidence if e.provenance.rule_id == rule_id]

    def by_direction(self, direction: Direction) -> list[Evidence]:
        return [e for e in self.evidence if e.direction == direction]

    def summary(self) -> dict:
        return {
            "when": self.when.isoformat(),
            "evidence_count": len(self.evidence),
            "adverse_count": len(self.by_direction(Direction.ADVERSE)),
            "protective_count": len(self.by_direction(Direction.PROTECTIVE)),
            "contradictions": len(self.contradictions),
            "rules_evaluated": self.rules_evaluated,
            "rules_failed": self.rules_failed,
        }


def build_family_report(chart, when: datetime) -> FamilyReport:
    """Evaluate all family rules against a chart at a given moment."""
    report = FamilyReport(when=when)

    rule_fns = [
        ("FAMILY-HOUSE-LORD-NATAL-001",
         lambda: family_rules.rule_family_lord_natal(chart)),
        ("FAMILY-SIGNIFICATOR-NATAL-001",
         lambda: family_rules.rule_family_significator_natal(chart)),
        ("FAMILY-RELATIONSHIP-001",
         lambda: family_rules.rule_family_relationship(chart)),
        ("FAMILY-LORD-DASHA-001",
         lambda: family_rules.rule_family_lord_dasha(chart, when)),
        ("FAMILY-UPAGRAHA-001",
         lambda: family_rules.rule_family_upagraha_placement(chart)),
        ("FAMILY-YAMAKANTAKA-PROTECT-001",
         lambda: family_rules.rule_family_yamakantaka_protective(chart, when)),
        ("FAMILY-YOGA-PROMOTION-001",
         lambda: family_rules.rule_family_yoga_promotion(chart)),
        ("FAMILY-D9-RECONCILIATION-001",
         lambda: family_rules.rule_family_d9_reconciliation(chart)),
        ("FAMILY-GOCHARA-001",
         lambda: family_rules.rule_family_gochara(chart, when)),
    ]

    for rule_id, fn in rule_fns:
        try:
            items = fn()
        except Exception as exc:
            report.rules_failed.append(f"{rule_id}: {exc}")
            continue
        report.rules_evaluated.append(rule_id)
        report.evidence.extend(items)

    report.contradictions = _detect_contradictions(report.evidence)
    return report


# Backwards-compatible alias so existing imports keep working.
build_FAMILY_report = build_family_report


# Backwards-compatible aliases so existing imports keep working.
FAMILYReport = FamilyReport
build_FAMILY_report = build_family_report
