from __future__ import annotations

from dataclasses import dataclass

from futurelens.grahas.nakshatra import NakshatraPosition


@dataclass(frozen=True)
class GrahaPosition:
    """A single graha's position in the natal chart."""

    name: str
    longitude: float               # sidereal, 0..360
    sign_index: int                # 0..11
    degree_in_sign: float          # 0..30
    nakshatra: NakshatraPosition
    retrograde: bool
    combust: bool
    house: int | None = None       # filled in by the chart assembler
