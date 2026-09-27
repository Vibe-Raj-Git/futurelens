from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChartContext:
    """Minimal context the Upagraha Engine needs. Whole-sign houses."""

    birth_datetime: datetime
    latitude: float
    longitude: float
    ascendant_sign_index: int
    house_signs: dict[int, int]
    house_lords: dict[int, str]
    graha_longitudes: dict[str, float]
    sunrise: datetime
    sunset: datetime
    ashtakavarga_bindus: dict[int, int] | None = None
