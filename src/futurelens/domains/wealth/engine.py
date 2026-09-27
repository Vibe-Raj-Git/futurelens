"""
Wealth domain engine.

Runs the wealth evidence rules against a chart and returns a
structured WealthReport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from futurelens.domains.wealth import rules as wealth_rules
from futurelens.evidence.graph import Contradiction, _detect_contradictions
from futurelens.models.evidence import Direction, Evidence


@dataclass
class WealthReport:
    """The wealth-domain evidence for a chart at a given moment."""

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
        """Compact summary for the LLM or UI."""
        return {
            "when": self.when.isoformat(),
            "evidence_count": len(self.evidence),
            "adverse_count": len(self.by_direction(Direction.ADVERSE)),
            "protective_count": len(self.by_direction(Direction.PROTECTIVE)),
            "contradictions": len(self.contradictions),
            "rules_evaluated": self.rules_evaluated,
            "rules_failed": self.rules_failed,
        }


def build_wealth_report(chart, when: datetime) -> WealthReport:
    """
    Evaluate all wealth rules against a chart at a given moment.
    """
    report = WealthReport(when=when)

    rule_fns = [
        ("WEALTH-HOUSE-LORD-NATAL-001", lambda: wealth_rules.rule_wealth_lord_natal(chart)),
        ("WEALTH-SIGNIFICATOR-NATAL-001", lambda: wealth_rules.rule_wealth_significator_natal(chart)),
        ("WEALTH-LORD-DASHA-001", lambda: wealth_rules.rule_wealth_lord_dasha(chart, when)),
        ("WEALTH-UPAGRAHA-001", lambda: wealth_rules.rule_wealth_upagraha_placement(chart)),
        ("WEALTH-YAMAKANTAKA-PROTECT-001", lambda: wealth_rules.rule_wealth_yamakantaka_protective(chart, when)),
        ("WEALTH-YOGA-PROMOTION-001", lambda: wealth_rules.rule_wealth_yoga_promotion(chart)),
        ("WEALTH-D9-RECONCILIATION-001", lambda: wealth_rules.rule_wealth_d9_reconciliation(chart)),
        ("WEALTH-GOCHARA-001", lambda: wealth_rules.rule_wealth_gochara(chart, when)),
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
