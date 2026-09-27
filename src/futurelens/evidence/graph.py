"""
Evidence graph aggregator.

Runs a set of rules against a chart, collects evidence, detects
contradictions, and exposes a structured result.

Contradiction detection works on SUBJECTS, not just domains. Two
evidence items contradict only if they:

  1. are in the same domain
  2. have opposite directions (ADVERSE vs PROTECTIVE)
  3. refer to the same subject (derived from the notes)

Subjects are extracted from evidence notes with a small set of
recognised keys:

  graha=<NAME>
  house=<N>
  upagraha=<NAME>
  transit_graha=<NAME>

If no subject can be derived, the item is not eligible for
contradiction pairing - it is a standalone observation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from futurelens.evidence.rules.base import EvidenceContext, EvidenceRule
from futurelens.evidence.rules.natal_placement import NatalPlacementRule
from futurelens.evidence.rules.sade_sati import SadeSatiRule
from futurelens.evidence.rules.upagraha_dasha import UpagrahaDashaRule
from futurelens.models.evidence import Direction, Evidence


DEFAULT_RULES: tuple[type, ...] = (
    UpagrahaDashaRule,
    SadeSatiRule,
    NatalPlacementRule,
)


SUBJECT_KEYS = ("graha", "house", "upagraha", "transit_graha")


@dataclass
class Contradiction:
    """A pair of evidence items with the same subject and opposite directions."""

    subject: str
    rule_id_a: str
    rule_id_b: str
    direction_a: str
    direction_b: str
    note: str


@dataclass
class EvidenceGraph:
    """The result of evaluating rules against a chart at a moment."""

    when: datetime
    domain: str | None
    evidence: list[Evidence] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    rules_evaluated: list[str] = field(default_factory=list)
    rules_failed: list[str] = field(default_factory=list)

    def by_rule(self, rule_id: str) -> list[Evidence]:
        return [e for e in self.evidence if e.provenance.rule_id == rule_id]

    def by_direction(self, direction: Direction) -> list[Evidence]:
        return [e for e in self.evidence if e.direction == direction]

    def by_domain(self, domain: str) -> list[Evidence]:
        return [e for e in self.evidence if e.domain == domain]


def _notes_to_dict(notes: tuple[str, ...]) -> dict[str, str]:
    """Convert ('key=value', ...) notes into a dict."""
    result: dict[str, str] = {}
    for n in notes:
        if "=" in n:
            k, v = n.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def _layer_of(rule_id: str) -> str:
    """
    Return the evidence layer implied by a rule ID.

    Classical Jyotish operates on distinct planes:
      natal   - the chart's promise (D1, vargas, yogas, upagrahas)
      dasha   - the running period
      transit - the current sky (Gochara)

    These planes do not contradict each other. They describe
    different realities of the same graha. Only items in the
    same layer can be in tension.
    """
    if rule_id.endswith("-GOCHARA-001"):
        return "transit"
    if rule_id.endswith("-DASHA-001"):
        return "dasha"
    return "natal"


def _subject_of(evidence: Evidence) -> str | None:
    """
    Derive a subject key from the evidence item's notes, prefixed
    by the evidence layer.

    Two items can only contradict if they share the same layer AND
    the same subject within that layer. This prevents spurious
    pairs such as a natal D9 item and a Gochara transit item being
    reported as contradictory.

    Priority order (within a layer):
      1. upagraha=<NAME>            -> "<layer>:upagraha:NAME"
      2. graha=<NAME>,house=<N>     -> "<layer>:graha:NAME@house:N"
      3. graha=<NAME>               -> "<layer>:graha:NAME"
      4. transit_graha=<NAME>       -> "<layer>:transit:NAME"
      5. house=<N>                  -> "<layer>:house:N"

    Returns None if no subject can be derived.
    """
    notes = _notes_to_dict(evidence.notes)
    layer = _layer_of(evidence.provenance.rule_id)
    prefix = f"{layer}:"

    if "upagraha" in notes:
        return f"{prefix}upagraha:{notes['upagraha']}"

    if "graha" in notes:
        if "house" in notes:
            return f"{prefix}graha:{notes['graha']}@house:{notes['house']}"
        return f"{prefix}graha:{notes['graha']}"

    if "transit_graha" in notes:
        return f"{prefix}transit:{notes['transit_graha']}"

    if "house" in notes:
        return f"{prefix}house:{notes['house']}"

    return None


def _detect_contradictions(
    evidence: list[Evidence],
) -> list[Contradiction]:
    """
    Find pairs of evidence items that:
      - are in the same domain
      - have opposite directions
      - share the same subject
    """
    contradictions: list[Contradiction] = []

    # Bucket by (domain, subject).
    buckets: dict[tuple, dict[str, list[Evidence]]] = {}
    for e in evidence:
        subject = _subject_of(e)
        if subject is None:
            continue  # standalone observation, not eligible
        key = (e.domain, subject)
        buckets.setdefault(key, {"ADVERSE": [], "PROTECTIVE": []})
        if e.direction == Direction.ADVERSE:
            buckets[key]["ADVERSE"].append(e)
        elif e.direction == Direction.PROTECTIVE:
            buckets[key]["PROTECTIVE"].append(e)

    for (domain, subject), bucket in buckets.items():
        for a in bucket["ADVERSE"]:
            for b in bucket["PROTECTIVE"]:
                contradictions.append(Contradiction(
                    subject=subject,
                    rule_id_a=a.provenance.rule_id,
                    rule_id_b=b.provenance.rule_id,
                    direction_a=a.direction.value,
                    direction_b=b.direction.value,
                    note=(
                        f"Opposite directions on {subject} "
                        f"in domain {domain or 'GENERAL'}"
                    ),
                ))

    return contradictions


def build_evidence_graph(
    ctx: EvidenceContext,
    rules: tuple[type, ...] | None = None,
) -> EvidenceGraph:
    """
    Run rules against the context, collect evidence, detect
    contradictions.
    """
    if rules is None:
        rules = DEFAULT_RULES

    graph = EvidenceGraph(when=ctx.when, domain=ctx.domain)

    all_evidence: list[Evidence] = []

    for rule_cls in rules:
        rule: EvidenceRule = rule_cls()
        if not rule.applies_to(ctx):
            continue
        try:
            items = rule.emit(ctx)
        except Exception as exc:
            graph.rules_failed.append(f"{rule.rule_id}: {exc}")
            continue
        graph.rules_evaluated.append(rule.rule_id)
        all_evidence.extend(items)

    if ctx.domain is not None:
        all_evidence = [
            e for e in all_evidence
            if e.domain is None or e.domain == ctx.domain
        ]

    graph.evidence = all_evidence
    graph.contradictions = _detect_contradictions(all_evidence)

    return graph
