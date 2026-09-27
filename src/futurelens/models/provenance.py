from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Provenance:
    """Every evidence item carries this. No exceptions."""

    rule_id: str
    rule_version: str
    tradition: str
    classical_basis: str
    calculation_method: str
    calculation_convention: str
    inputs: tuple[Any, ...] = field(default_factory=tuple)
    derived_values: tuple[Any, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
