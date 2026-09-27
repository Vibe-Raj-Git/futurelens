from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DashaMoment:
    """The active dasha chain at a moment in time."""

    when: datetime
    mahadasha_lord: str
    antardasha_lord: str
    pratyantardasha_lord: str | None
    mahadasha_start: datetime
    mahadasha_end: datetime
    antardasha_start: datetime
    antardasha_end: datetime
