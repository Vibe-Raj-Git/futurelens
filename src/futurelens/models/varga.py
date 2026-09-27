from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VargaPosition:
    """A graha's position in a divisional chart."""

    name: str
    d1_longitude: float
    d1_sign_index: int
    d1_dignity: str
    d9_sign_index: int
    d9_sign_name: str
    d9_degree_in_sign: float
    d9_longitude: float
    d9_dignity: str


@dataclass(frozen=True)
class VargaReport:
    """The result of computing a divisional chart for all grahas."""

    varga: str                       # "D9"
    name: str                        # "NAVAMSA"
    positions: dict[str, VargaPosition]


@dataclass(frozen=True)
class ReconciliationResult:
    """D1 vs D9 comparison for a single graha."""

    name: str
    d1_dignity: str
    d9_dignity: str
    category: str                    # CONFIRMED / UPGRADED / DOWNGRADED / NEUTRAL
    weight_tier: str                 # SUPPORTING / MODIFIER
    explanation: str