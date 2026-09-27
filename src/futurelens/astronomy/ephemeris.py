"""
Ephemeris provider interface and Swiss Ephemeris implementation.

Provides Sun longitude, sunrise, sunset, and planetary longitudes
for all Swiss Ephemeris bodies, including longitude speed for
retrograde detection.

The project stores Swiss Ephemeris data files in:

    <project_root>/ephe

The path is configured explicitly before every calculation so the
application does not depend on the machine-wide SE_EPHE_PATH setting.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path


class EphemerisProvider(ABC):
    """Abstract ephemeris interface."""

    @abstractmethod
    def sun_longitude(self, when: datetime) -> float:
        """Sidereal Sun longitude in degrees, 0..360."""

    @abstractmethod
    def sunrise(
        self,
        on_date: datetime,
        lat: float,
        lon: float,
    ) -> datetime:
        """Sunrise as tz-aware UTC datetime."""

    @abstractmethod
    def sunset(
        self,
        on_date: datetime,
        lat: float,
        lon: float,
    ) -> datetime:
        """Sunset as tz-aware UTC datetime."""


class SwissEphemerisProvider(EphemerisProvider):
    """
    Swiss Ephemeris implementation.

    Default ayanamsha:
        Swiss Ephemeris SIDM_TRUE_CITRA.

    The provider explicitly configures the project's local
    Swiss Ephemeris data directory before each calculation.

    Install:
        pip install pyswisseph
    """

    def __init__(self, ayanamsha_id: int | None = None) -> None:
        import swisseph as swe

        self._swe = swe

        # Project-local ephemeris data directory.
        #
        # This file is:
        #   <project_root>/src/futurelens/astronomy/ephemeris.py
        #
        # Therefore parents[3] resolves to:
        #   <project_root>
        project_root = Path(__file__).resolve().parents[3]
        self._ephe_path = project_root / "ephe"

        if not self._ephe_path.is_dir():
            raise FileNotFoundError(
                "Swiss Ephemeris data directory not found: "
                f"{self._ephe_path}"
            )

        self._ayanamsha_id = (
            ayanamsha_id
            if ayanamsha_id is not None
            else swe.SIDM_TRUE_CITRA
        )

        self._configure()

    def _configure(self) -> None:
        """
        Configure Swiss Ephemeris for this provider.

        This is intentionally called immediately before calculations
        because Swiss Ephemeris configuration is process-global.
        """

        self._swe.set_ephe_path(str(self._ephe_path))
        self._swe.set_sid_mode(self._ayanamsha_id)

    def _jd(self, when: datetime) -> float:
        """
        Convert a timezone-aware datetime to Julian Day UT.

        Naive datetimes are treated as UTC for backward compatibility.
        """

        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)

        when_utc = when.astimezone(timezone.utc)

        hour = (
            when_utc.hour
            + when_utc.minute / 60.0
            + when_utc.second / 3600.0
            + when_utc.microsecond / 3.6e9
        )

        return self._swe.julday(
            when_utc.year,
            when_utc.month,
            when_utc.day,
            hour,
        )

    def sun_longitude(self, when: datetime) -> float:
        """
        Return sidereal Sun longitude in degrees, 0..360.
        """

        self._configure()

        jd = self._jd(when)

        pos, _ = self._swe.calc_ut(
            jd,
            self._swe.SUN,
            self._swe.FLG_SIDEREAL,
        )

        return pos[0] % 360.0

    def planet_longitude(
        self,
        when: datetime,
        swe_id: int,
    ) -> tuple[float, float, bool]:
        """
        Return:

            (sidereal_longitude, longitude_speed, retrograde)

        for a Swiss Ephemeris body ID.

        FLG_SPEED is required for calc_ut to compute longitude speed.
        """

        self._configure()

        jd = self._jd(when)

        flags = (
            self._swe.FLG_SIDEREAL
            | self._swe.FLG_SPEED
        )

        pos, _ = self._swe.calc_ut(
            jd,
            swe_id,
            flags,
        )

        longitude = pos[0] % 360.0
        speed = pos[3]
        retrograde = speed < 0.0

        return longitude, speed, retrograde

    def _rise_or_set(
        self,
        on_date: datetime,
        lat: float,
        lon: float,
        flag: int,
    ) -> datetime:
        """
        Calculate sunrise or sunset and return a timezone-aware
        UTC datetime.
        """

        self._configure()

        if on_date.tzinfo is None:
            on_date = on_date.replace(tzinfo=timezone.utc)

        on_date_utc = on_date.astimezone(timezone.utc)

        jd_start = self._swe.julday(
            on_date_utc.year,
            on_date_utc.month,
            on_date_utc.day,
            0.0,
        )

        geopos = (
            lon,
            lat,
            0.0,
        )

        result, tret = self._swe.rise_trans(
            jd_start,
            self._swe.SUN,
            flag,
            geopos,
        )

        if result != 0:
            raise RuntimeError(
                f"rise_trans failed with code {result} for "
                f"{on_date_utc.date()} at ({lat}, {lon})."
            )

        jd_event = tret[0]

        year, month, day, hour = self._swe.revjul(jd_event)

        h = int(hour)

        m_full = (hour - h) * 60.0
        m = int(m_full)

        s = int((m_full - m) * 60.0)

        return datetime(
            year,
            month,
            day,
            h,
            m,
            s,
            tzinfo=timezone.utc,
        )

    def sunrise(
        self,
        on_date: datetime,
        lat: float,
        lon: float,
    ) -> datetime:
        """Return sunrise as timezone-aware UTC datetime."""

        return self._rise_or_set(
            on_date,
            lat,
            lon,
            self._swe.CALC_RISE
            | self._swe.BIT_DISC_CENTER,
        )

    def sunset(
        self,
        on_date: datetime,
        lat: float,
        lon: float,
    ) -> datetime:
        """Return sunset as timezone-aware UTC datetime."""

        return self._rise_or_set(
            on_date,
            lat,
            lon,
            self._swe.CALC_SET
            | self._swe.BIT_DISC_CENTER,
        )