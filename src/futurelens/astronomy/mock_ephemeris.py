from __future__ import annotations

from datetime import datetime

from futurelens.astronomy.ephemeris import EphemerisProvider


class MockEphemeris(EphemerisProvider):
    """Deterministic mock. Used only for tests. Not for production."""

    EPOCH = datetime(2000, 1, 1, 12, 0, 0)

    def sun_longitude(self, when: datetime) -> float:
        days = (when - self.EPOCH).total_seconds() / 86400.0
        return (days * 1.0) % 360.0

    def sunrise(self, on_date: datetime, lat: float, lon: float) -> datetime:
        return on_date.replace(hour=6, minute=0, second=0, microsecond=0)

    def sunset(self, on_date: datetime, lat: float, lon: float) -> datetime:
        return on_date.replace(hour=18, minute=0, second=0, microsecond=0)
