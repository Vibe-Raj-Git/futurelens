from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BAVResult:
    """Bhinnashtakavarga for one subject planet."""

    subject: str
    bindus_by_sign: tuple[int, ...]  # 12 values, one per sign
    total: int


@dataclass(frozen=True)
class SAVResult:
    """Sarvastakavarga - sum of all BAVs."""

    bindus_by_sign: tuple[int, ...]  # 12 values, one per sign
    total: int


@dataclass(frozen=True)
class AshtakavargaReport:
    """Complete Ashtakavarga computation."""

    bav: dict[str, BAVResult]
    sav: SAVResult

    def bindu_for_sign(self, sign_index: int) -> int:
        """SAV bindu count for a sign."""
        return self.sav.bindus_by_sign[sign_index]

    def bindu_for_house(self, house_signs: dict[int, int], house: int) -> int:
        """SAV bindu count for a house."""
        sign = house_signs[house]
        return self.sav.bindus_by_sign[sign]
