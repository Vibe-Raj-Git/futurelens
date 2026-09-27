"""
Template backend.

Deterministic, no external dependency. Produces a formatted
explanation from the evidence payload. It cannot hallucinate
citations because it only copies rule IDs from the evidence.
"""

from __future__ import annotations

from futurelens.llm.contract import LLMRequest, LLMResponse


class TemplateBackend:
    """Deterministic, no external dependency."""

    name = "template"

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = request.payload
        evidence = payload.get("evidence", [])
        contradictions = payload.get("contradictions", [])

        lines = []
        lines.append(
            f"Evidence for {payload['domain']} at {payload['when']}:"
        )
        lines.append("")

        protective = [e for e in evidence if e["direction"] == "PROTECTIVE"]
        adverse = [e for e in evidence if e["direction"] == "ADVERSE"]

        if protective:
            lines.append("Supportive indications:")
            for e in protective:
                lines.append(f"  - {_describe(e)}")
            lines.append("")

        if adverse:
            lines.append("Challenging indications:")
            for e in adverse:
                lines.append(f"  - {_describe(e)}")
            lines.append("")

        if contradictions:
            lines.append("Contradictions in the evidence:")
            for c in contradictions:
                lines.append(
                    f"  - {c['note']} "
                    f"[{c['rule_id_a']} vs {c['rule_id_b']}]"
                )
            lines.append("")

        if not evidence:
            lines.append("No evidence was produced for this domain.")

        text = "\n".join(lines).rstrip()
        rule_ids = tuple(sorted({e["rule_id"] for e in evidence}))

        return LLMResponse(
            text=text,
            rule_ids_cited=rule_ids,
            backend=self.name,
            raw={
                "valid_cited": list(rule_ids),
                "redacted_cited": [],
                "redacted_count": 0,
            },
        )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _describe(e: dict) -> str:
    """
    Produce a deterministic human-readable sentence for one
    evidence item, ending with the rule ID in square brackets.

    The rule author has already populated finding and interpretation
    at emission time. This function concatenates them.
    """
    rid = e.get("rule_id", "")
    finding = (e.get("finding") or "").strip()
    interpretation = (e.get("interpretation") or "").strip()

    parts = []
    if finding:
        parts.append(finding)
    if interpretation and interpretation.lower() not in finding.lower():
        parts.append(interpretation)

    body = " ".join(parts) if parts else "Evidence item."
    return f"{body} [{rid}]"
