"""
Prompt builder.

Converts deterministic FutureLens evidence into semantic evidence
before sending it to an LLM.

The deterministic astrology engine remains the source of truth.

This layer translates internal engine fields into human-readable
findings. The LLM explains those findings; it does not decode the
engine's internal representation or perform new astrological
calculations.

Architecture boundary
---------------------

Deterministic engine
        |
        v
Evidence objects
        |
        v
Semantic evidence translation  <-- this module
        |
        v
LLMRequest
        |
        v
LLM backend
        |
        v
Human-readable explanation

The LLM is therefore an evidence explainer, not an astrology engine.
"""

from __future__ import annotations

import json

from futurelens.llm.contract import LLMRequest, assert_payload_safe
from futurelens.models.evidence import Evidence


SYSTEM_PROMPT = """You are an evidence explainer for FutureLens, a deterministic Jyotish
forecasting engine.

You do NOT generate astrology. You explain evidence that has already
been produced by a classical rule engine.

================================================================
HOW TO READ THE EVIDENCE
================================================================

Every evidence item you receive carries a weight tier:

  STRUCTURAL - the fundamental promise of the chart. Lordships,
      yogas, own-sign placements, Lagna strength. This is the
      reading.

  SUPPORTING - secondary indicators. Reinforce or qualify the
      structural picture. Dasha activation. Benign placements in
      favourable houses.

  MODIFIER   - adjustments at the margins. Combustion, Upagrahas,
      transits, debilitation. Cannot override structural evidence.

These tiers are not equal.

Volume does not equal importance. One STRUCTURAL item outweighs
many MODIFIERs. A chart with three STRUCTURAL findings and ten
MODIFIERs is a chart with three important things to say, plus
caveats.

Structure your reading in this order:

  1. Open with the single strongest STRUCTURAL finding. State it
     first, plainly. That is the headline of the chart.

  2. Present the remaining STRUCTURAL findings.

  3. Present the SUPPORTING findings that qualify or reinforce the
     structural picture.

  4. Close with the MODIFIER findings as a short caveat paragraph.
     Do not enumerate them one by one. Group them. Say "several
     modifiers qualify the picture" and describe them briefly.

A reading that lists every item equally is a report, not a reading.
Produce a reading.

================================================================
EVIDENCE IS THE SOURCE OF TRUTH
================================================================

Every evidence item carries three fields:

  subject         what the item is about
  finding         the plain-English fact
  interpretation  why it matters

These three fields are authoritative. They were produced by the
deterministic engine. Treat them as the facts of this reading.

Do not decode internal engine fields. Do not reinterpret numeric
house or sign codes. Do not infer meanings from hidden
implementation details. Do not perform new astrological
calculations.

Do not fill gaps using general astrology knowledge. If a claim is
not supported by a supplied evidence item, omit the claim.

The classical_basis field names the traditional source the engine
used. It is context. It does not authorize you to reconstruct
additional rules from that tradition.

================================================================
CITATION CONTRACT
================================================================

Every substantive astrological claim must cite at least one rule_id
that appears VERBATIM in the evidence payload.

You may ONLY cite rule IDs present in the evidence.

NEVER invent, modify, shorten, normalize, or fabricate rule IDs.
Never cite a rule that "should" exist. If a claim is not supported
by a supplied rule ID, omit the claim.

Citation format: [RULE-ID]

The text inside brackets must match exactly.

When several evidence items share a rule ID, cite the rule once for
the group. Do not repeat the same citation on every sentence.

================================================================
DIRECTION
================================================================

Every evidence item carries a direction:

  PROTECTIVE    favourable
  ADVERSE       challenging
  CONTEXT_INCOMPLETE  missing a required input

Respect the supplied direction. Do not convert PROTECTIVE into a
guaranteed positive outcome, ADVERSE into a guaranteed negative
outcome, or either into neutrality.

Use cautious language: indicates, suggests, is treated as, points
toward, is classified as.

================================================================
CONTRADICTIONS
================================================================

Do not average contradictory evidence. Do not cancel one indication
against another. Preserve the tension.

If two items point in opposite directions, name both, explain what
each indicates, and stop there. Do not convert the combination into
a numerical or qualitative net result.

================================================================
NO EVENT PREDICTIONS
================================================================

Do not predict specific real-world events. Do not state that
something "will happen", "must happen", or "is certain to happen".

Do not invent dates, time periods, financial amounts, transactions,
career events, relationship events, health events, investment
outcomes, market outcomes, or any other concrete future event
unless the timing or outcome is explicitly supplied as evidence.

Explain classical indications. Do not turn them into guaranteed
outcomes.

================================================================
QUESTION HANDLING
================================================================

The user's question, if supplied, controls emphasis only. It does
not create new evidence, authorize additional astrology, or
override the evidence.

If the question asks about something the evidence does not
establish, say so plainly. Do not answer unsupported questions by
relying on general astrology knowledge.

================================================================
STYLE
================================================================

Use plain, natural language. Avoid unnecessary Jyotish jargon;
when a technical term is needed, explain it briefly.

Do not pad sparse evidence. Do not repeat the same point.

Prefer paragraph form over bullet lists. A reading that reads like
prose is better than one that reads like a checklist.

Aim for four to six paragraphs. Longer than six paragraphs means
you are enumerating rather than prioritizing.

================================================================
OUTPUT
================================================================

Return plain text only. Do not return JSON.

You will receive a JSON payload with:

  domain          the life area being read
  when            the target moment
  question        the user's question, if any
  evidence        list of evidence items
  contradictions  list of contradictions, if any

Each evidence item contains:

  rule_id, rule_version, tradition, classical_basis
  direction, domain, weight
  subject, finding, interpretation

Explain the supplied findings clearly, with the weight hierarchy
in mind, and cite every substantive claim.
"""



def _semantic_evidence(e: Evidence) -> dict:
    """
    Convert deterministic engine evidence into semantic evidence.

    The rule author has already populated subject / finding /
    interpretation at emission time. This function is a pass-through
    that assembles the payload for the LLM. It does not parse notes
    and does not reconstruct semantic text from rule IDs.

    If a rule has not populated the semantic fields (should not
    happen after Phase 3), fall back to the notes-only representation
    so the LLM still receives something usable.
    """
    if e.is_semantic():
        return {
            "rule_id": e.provenance.rule_id,
            "rule_version": e.provenance.rule_version,
            "tradition": e.provenance.tradition,
            "classical_basis": e.provenance.classical_basis,
            "direction": e.direction.value,
            "domain": e.domain,
            "weight": e.weight.value,
            "subject": e.subject,
            "finding": e.finding,
            "interpretation": e.interpretation,
        }

    # Defensive fallback for unmigrated rules.
    return {
        "rule_id": e.provenance.rule_id,
        "rule_version": e.provenance.rule_version,
        "tradition": e.provenance.tradition,
        "classical_basis": e.provenance.classical_basis,
        "direction": e.direction.value,
        "domain": e.domain,
        "weight": e.weight.value,
        "subject": "Astrological indication",
        "finding": "The deterministic engine produced an indication.",
        "interpretation": (
            "Consider together with the other evidence."
        ),
    }


def _contradiction_to_payload(c) -> dict:
    """
    Convert a deterministic contradiction into the LLM-safe payload.
    """
    return {
        "subject": c.subject,
        "rule_id_a": c.rule_id_a,
        "direction_a": c.direction_a,
        "rule_id_b": c.rule_id_b,
        "direction_b": c.direction_b,
        "note": c.note,
    }


def build_request(
    report,
    question: str | None = None,
) -> LLMRequest:
    """
    Build an LLMRequest from a domain report.

    The report remains the source of truth.

    Only semantic evidence is exposed to the LLM. Raw deterministic
    engine notes are not included in the payload.
    """
    semantic_evidence = []
    for e in report.evidence:
        item = _semantic_evidence(e)
        if item is not None:
            semantic_evidence.append(item)

    payload = {
        "domain": _infer_domain(report),
        "when": report.when.isoformat(),
        "question": question,
        "evidence": semantic_evidence,
        "contradictions": [
            _contradiction_to_payload(c)
            for c in report.contradictions
        ],
    }

    # Final safety check before the payload is handed to a backend.
    assert_payload_safe(payload)

    user_prompt = _build_user_prompt(
        payload,
        question,
    )

    return LLMRequest(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        payload=payload,
        domain=payload["domain"],
        when_iso=payload["when"],
    )


def _infer_domain(report) -> str:
    """Infer the domain from the deterministic evidence."""
    for e in report.evidence:
        if e.domain:
            return e.domain

    return "GENERAL"


def _build_user_prompt(
    payload: dict,
    question: str | None,
) -> str:
    """
    Build the user prompt.

    Gemini receives semantic evidence rather than raw engine notes.

    The complete semantic evidence is included as JSON so the backend
    receives exactly the same evidence that was validated by the
    deterministic layer.
    """
    lines = [
        f"Domain: {payload['domain']}",
        f"Moment: {payload['when']}",
    ]

    if question:
        lines.append(f"Question: {question}")

    lines.append("")

    # ---------------------------------------------------------------
    # Semantic evidence
    # ---------------------------------------------------------------
    lines.append("Semantic evidence supplied by the deterministic engine:")
    lines.append("```json")

    lines.append(
        json.dumps(
            {
                "evidence": payload["evidence"],
                "contradictions": payload["contradictions"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    lines.append("```")
    lines.append("")

    # ---------------------------------------------------------------
    # Valid rule IDs
    #
    # A set is deliberately used here because the same rule_id may
    # legitimately occur on multiple evidence items.
    # ---------------------------------------------------------------
    valid_ids = sorted(
        {
            e["rule_id"]
            for e in payload["evidence"]
            if e.get("rule_id")
        }
    )

    lines.append(
        "Valid rule IDs you may cite (and ONLY these rule IDs):"
    )

    for rid in valid_ids:
        lines.append(f"  - {rid}")

    lines.append("")

    # ---------------------------------------------------------------
    # Response instructions
    # ---------------------------------------------------------------
    lines.append(
        f"Explain the {len(payload['evidence'])} semantic evidence "
        "items in clear, concise language."
    )

    if payload["contradictions"]:
        lines.append(
            f"There are {len(payload['contradictions'])} contradictions. "
            "Preserve and explain them rather than averaging them away."
        )

    lines.append(
        "The semantic fields 'subject', 'finding', and 'interpretation' "
        "are authoritative. Explain them without reconstructing hidden "
        "engine logic."
    )

    lines.append(
        "Do not introduce astrological claims that are not supported "
        "by the supplied evidence."
    )

    lines.append(
        "The user's question changes emphasis only. It does not create "
        "new evidence."
    )

    lines.append(
        "Cite every substantive astrological claim inline using the "
        "exact [RULE-ID] notation."
    )

    lines.append(
        "Use only rule IDs from the valid rule ID list above."
    )

    lines.append(
        "Do not predict specific real-world events, outcomes, dates, "
        "or timings unless they are explicitly present in the evidence."
    )

    return "\n".join(lines)