"""
The rule protocol.

Every evidence rule implements this interface. A rule is:

  - named by a rule_id
  - anchored to a classical source (basis)
  - versioned
  - able to say whether it applies (applies_to)
  - able to produce evidence items (emit)

A rule receives an EvidenceContext (a chart plus a target moment)
and produces a list of Evidence objects. Rules never read raw
ephemeris data. They read from the Chart and from the DashaMoment
and TransitReport that the chart already computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from futurelens.models.evidence import Evidence
from futurelens.models.provenance import Provenance


# Forward reference: the Chart type is defined in futurelens.chart,
# but we do not import it here to avoid a circular import.


@dataclass(frozen=True)
class EvidenceContext:
    """
    Everything a rule needs to evaluate itself.

    Attributes
    ----------
    chart : futurelens.chart.Chart
        The natal chart.
    when : datetime
        The moment for which evidence is being produced.
    domain : str | None
        Optional domain filter (e.g. "WEALTH"). Rules may ignore
        this; the graph aggregator applies it after emission.
    """

    chart: object
    when: datetime
    domain: str | None = None


class EvidenceRule(Protocol):
    """Every evidence rule implements this."""

    rule_id: str
    rule_version: str
    tradition: str
    classical_basis: str
    calculation_method: str
    calculation_convention: str

    def applies_to(self, ctx: EvidenceContext) -> bool:
        """Return True if this rule can be evaluated for the context."""
        ...

    def emit(self, ctx: EvidenceContext) -> list[Evidence]:
        """Return evidence items triggered by the rule, or empty list."""
        ...


def make_provenance(
    rule_id: str,
    classical_basis: str,
    calculation_method: str,
    calculation_convention: str = "PHALADEEPIKA_25",
    rule_version: str = "0.1",
    tradition: str = "PHALADEEPIKA",
) -> Provenance:
    """Helper to build a Provenance for a rule."""
    return Provenance(
        rule_id=rule_id,
        rule_version=rule_version,
        tradition=tradition,
        classical_basis=classical_basis,
        calculation_method=calculation_method,
        calculation_convention=calculation_convention,
    )
