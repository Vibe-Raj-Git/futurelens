from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from futurelens.models.graha import GrahaPosition


@dataclass(frozen=True)
class TransitPosition:
    """A single graha's transit position relative to a natal chart."""

    graha: GrahaPosition
    house_from_lagna: int
    house_from_moon: int
    house_from_moon_nakshatra: int
    # SAV bindu value for the sign the transit occupies (if available).
    sav_bindus: int | None = None
    sav_strength: str | None = None


@dataclass(frozen=True)
class TransitReport:
    """Complete transit snapshot at a given moment."""

    when: datetime
    positions: dict[str, TransitPosition]
