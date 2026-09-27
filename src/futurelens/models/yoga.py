from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class YogaResult:
    """The result of detecting one yoga in a chart."""

    yoga_id: str
    yoga_name: str
    classical_basis: str
    present: bool
    conditions_met: tuple[str, ...] = ()
    conditions_failed: tuple[str, ...] = ()
    involved_grahas: tuple[str, ...] = ()
    involved_houses: tuple[int, ...] = ()
    notes: tuple[str, ...] = ()
