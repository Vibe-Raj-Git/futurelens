from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UpagrahaName(str, Enum):
    GULIKA = "GULIKA"
    YAMAKANTAKA = "YAMAKANTAKA"
    KALA = "KALA"
    ARDHAPRAHARA = "ARDHAPRAHARA"
    MRITYU = "MRITYU"
    DHUMA = "DHUMA"
    VYATIPATA = "VYATIPATA"
    PARIVESHA = "PARIVESHA"
    INDRACHAPA = "INDRACHAPA"
    UPAKETU = "UPAKETU"


class UpagrahaFamily(str, Enum):
    KALAVELA = "KALAVELA"
    SUN_DERIVED = "SUN_DERIVED"


@dataclass(frozen=True)
class UpagrahaPosition:
    """Deterministic output of the calculation layer."""

    name: UpagrahaName
    family: UpagrahaFamily
    longitude: float
    sign_index: int
    degree_in_sign: float
    house: int | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.longitude < 360.0:
            raise ValueError(
                f"Longitude must be in [0, 360); got {self.longitude}"
            )
