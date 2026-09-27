"""
Cast a chart from birth data.

Public entry point of FutureLens. Produces a fully resolved Chart
with ascendant, houses, grahas, Upagrahas, Dasha, transit query,
evidence graph, wealth and career domain reports, yoga detection,
Ashtakavarga, and LLM-ready explanations.

Ayanamsha handling
------------------
The chart-level convention is the single source of truth for
ayanamsha selection.

The default convention is True Chitrapaksha / Swiss Ephemeris
SIDM_TRUE_CITRA. The same ayanamsha is passed to:

    1. Ascendant calculation
    2. Swiss Ephemeris planetary calculations

This prevents the ascendant and graha calculations from silently
using different ayanamsha models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from futurelens.astronomy.ascendant import (
    AscendantResult,
    compute_ascendant,
)
from futurelens.astronomy.ephemeris import SwissEphemerisProvider
from futurelens.conventions import Conventions
from futurelens.dasha.definitions import DashaPeriod
from futurelens.dasha.engine import (
    active_period,
    compute_antardashas,
    compute_mahadashas,
    compute_pratyantardashas,
)
from futurelens.grahas.engine import compute_grahas
from futurelens.houses.resolver import HouseChart, resolve_houses
from futurelens.models.chart import ChartContext
from futurelens.models.dasha import DashaMoment
from futurelens.models.graha import GrahaPosition
from futurelens.models.transit import TransitReport
from futurelens.transits.engine import compute_transits
from futurelens.upagraha.engine import UpagrahaEngine, UpagrahaReport


@dataclass(frozen=True)
class Chart:
    """A fully resolved chart."""

    birth_datetime: datetime
    latitude: float
    longitude: float
    ascendant: AscendantResult
    houses: HouseChart
    grahas: dict[str, GrahaPosition]
    sun_longitude: float
    sunrise: datetime
    sunset: datetime
    upagrahas: UpagrahaReport
    mahadashas: list[DashaPeriod]
    conventions: Conventions

    def house_of_longitude(self, longitude: float) -> int:
        """Return the whole-sign house containing a longitude."""
        return self.houses.house_of_sign(int(longitude // 30))

    def house_of_graha(self, name: str) -> int:
        """Return the natal house occupied by a graha."""
        return self.houses.house_of_sign(
            self.grahas[name].sign_index
        )

    def house_of_upagraha(self, name: str) -> int | None:
        """Return the natal house occupied by an Upagraha."""
        pos = self.upagrahas.positions.get(name)
        return pos.house if pos else None

    def dasha_at(self, when: datetime) -> DashaMoment:
        """
        Return the active Mahadasha, Antardasha and Pratyantardasha
        at the supplied datetime.
        """
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)

        days = (
            when - self.birth_datetime
        ).total_seconds() / 86400.0

        md = active_period(self.mahadashas, days)

        if md is None:
            raise ValueError(
                f"Date {when} is outside the 120-year dasha range."
            )

        ad_list = compute_antardashas(md)
        ad = active_period(ad_list, days)

        if ad is None:
            raise ValueError(
                "Antardasha not found — internal error."
            )

        pd_list = compute_pratyantardashas(ad)
        pd = active_period(pd_list, days)

        def to_dt(days_since_birth: float) -> datetime:
            return self.birth_datetime + timedelta(
                days=days_since_birth
            )

        return DashaMoment(
            when=when,
            mahadasha_lord=md.lord,
            antardasha_lord=ad.lord,
            pratyantardasha_lord=pd.lord if pd else None,
            mahadasha_start=to_dt(md.start_days),
            mahadasha_end=to_dt(md.end_days),
            antardasha_start=to_dt(ad.start_days),
            antardasha_end=to_dt(ad.end_days),
        )

    def ashtakavarga(self):
        """
        Compute and return the Ashtakavarga report.

        The result is cached on the instance so that multiple
        consumers (the domain rules that annotate houses with SAV
        bindus, the transit engine, the Gochara engine) do not
        each trigger a fresh computation.
        """
        cached = getattr(self, "_ashtakavarga_cache", None)
        if cached is not None:
            return cached

        from futurelens.ashtakavarga.engine import (
            compute_ashtakavarga,
        )

        result = compute_ashtakavarga(self)
        object.__setattr__(self, "_ashtakavarga_cache", result)
        return result

    def transits_at(self, when: datetime) -> TransitReport:
        """
        Compute transit report for the supplied datetime.

        Transit interpretation uses the natal ascendant, natal Moon,
        Moon nakshatra and natal Sarvashtakavarga bindus.
        """
        ashtaka = self.ashtakavarga()

        return compute_transits(
            when=when,
            natal_ascendant_sign=self.ascendant.sign_index,
            natal_moon_sign=self.grahas["MOON"].sign_index,
            natal_moon_nakshatra_index=(
                self.grahas["MOON"]
                .nakshatra
                .nakshatra_index
            ),
            sav_bindus=ashtaka.sav.bindus_by_sign,
        )

    def evidence(
        self,
        when: datetime,
        domain: str | None = None,
    ):
        """Build the evidence graph for the supplied domain."""
        from futurelens.evidence.graph import (
            build_evidence_graph,
        )
        from futurelens.evidence.rules.base import (
            EvidenceContext,
        )

        ctx = EvidenceContext(
            chart=self,
            when=when,
            domain=domain,
        )

        return build_evidence_graph(ctx)

    def wealth(self, when: datetime):
        """Build the wealth-domain report."""
        from futurelens.domains.wealth.engine import (
            build_wealth_report,
        )

        return build_wealth_report(self, when)

    def career(self, when: datetime):
        """Build the career-domain report."""
        from futurelens.domains.career.engine import (
            build_career_report,
        )

        return build_career_report(self, when)

    def yogas(self):
        """Detect the supported natal yogas."""
        from futurelens.yogas.detector import detect_yogas

        return detect_yogas(self)

    def explain_wealth(
        self,
        when: datetime,
        question: str | None = None,
        backend=None,
    ):
        """Generate an LLM-ready explanation of the wealth report."""
        from futurelens.llm.explainer import explain

        report = self.wealth(when)

        return explain(
            report,
            question=question,
            backend=backend,
        )

    def explain_career(
        self,
        when: datetime,
        question: str | None = None,
        backend=None,
    ):
        """Generate an LLM-ready explanation of the career report."""
        from futurelens.llm.explainer import explain

        report = self.career(when)

        return explain(
            report,
            question=question,
            backend=backend,
        )


def cast_chart(
    when: datetime,
    latitude: float,
    longitude: float,
    conventions: Conventions | None = None,
) -> Chart:
    """
    Cast a complete Vedic astrology chart from birth data.

    The supplied Conventions object controls calculation conventions,
    including ayanamsha.

    If no Conventions object is supplied, the project's default
    convention is used. This should be True Chitrapaksha /
    Swiss Ephemeris SIDM_TRUE_CITRA.

    The selected ayanamsha is explicitly passed to both the
    ascendant calculator and the planetary ephemeris provider so
    that all sidereal calculations use the same model.
    """

    # ------------------------------------------------------------------
    # 1. Normalize datetime
    # ------------------------------------------------------------------

    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    # ------------------------------------------------------------------
    # 2. Resolve and validate calculation conventions
    # ------------------------------------------------------------------

    if conventions is None:
        conventions = Conventions()

    conventions.validate()

    # ------------------------------------------------------------------
    # 3. Resolve Swiss Ephemeris ayanamsha
    # ------------------------------------------------------------------
    #
    # The Conventions enum is deliberately kept independent of the
    # Swiss Ephemeris implementation. Therefore the mapping from the
    # domain convention to the Swiss Ephemeris constant is performed
    # here.
    #
    # Currently the project supports:
    #
    #     Ayanamsha.TRUE_CITRA -> swe.SIDM_TRUE_CITRA
    #
    # If additional ayanamshas are introduced later, extend the
    # mapping here rather than silently falling back to Lahiri.
    # ------------------------------------------------------------------

    import swisseph as swe

    ayanamsha_map = {
        "TRUE_CITRA": swe.SIDM_TRUE_CITRA,
        "LAHIRI": swe.SIDM_LAHIRI,
    }

    ayanamsha_name = conventions.ayanamsha.value

    try:
        ayanamsha_id = ayanamsha_map[ayanamsha_name]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported ayanamsha convention: {ayanamsha_name!r}. "
            f"Supported values: {sorted(ayanamsha_map)}"
        ) from exc

    # ------------------------------------------------------------------
    # 4. Create the ephemeris provider with the selected ayanamsha
    # ------------------------------------------------------------------

    eph = SwissEphemerisProvider(
        ayanamsha_id=ayanamsha_id
    )

    # ------------------------------------------------------------------
    # 5. Compute ascendant
    # ------------------------------------------------------------------

    asc = compute_ascendant(
        when,
        latitude=latitude,
        longitude=longitude,
        sidereal=True,
        ayanamsha_id=ayanamsha_id,
    )

    # ------------------------------------------------------------------
    # 6. Resolve whole-sign houses from ascendant
    # ------------------------------------------------------------------

    houses = resolve_houses(asc.sign_index)

    # ------------------------------------------------------------------
    # 7. Compute grahas using the SAME ayanamsha
    # ------------------------------------------------------------------

    grahas = compute_grahas(
        when,
        ephemeris=eph,
    )

    # ------------------------------------------------------------------
    # 8. Attach whole-sign houses to graha positions
    # ------------------------------------------------------------------

    grahas_with_houses = {
        name: GrahaPosition(
            name=pos.name,
            longitude=pos.longitude,
            sign_index=pos.sign_index,
            degree_in_sign=pos.degree_in_sign,
            nakshatra=pos.nakshatra,
            retrograde=pos.retrograde,
            combust=pos.combust,
            house=houses.house_of_sign(pos.sign_index),
        )
        for name, pos in grahas.items()
    }

    # ------------------------------------------------------------------
    # 9. Sun longitude
    # ------------------------------------------------------------------

    sun_lon = grahas_with_houses["SUN"].longitude

    # ------------------------------------------------------------------
    # 10. Sunrise / sunset
    # ------------------------------------------------------------------

    #
    # Sunrise and sunset are astronomical events and do not depend
    # on sidereal ayanamsha. The ephemeris provider still handles
    # the calculation so the astronomy implementation remains
    # centralized.
    #

    utc_date = when.astimezone(timezone.utc)

    sunrise = eph.sunrise(
        utc_date,
        latitude,
        longitude,
    )

    sunset = eph.sunset(
        utc_date,
        latitude,
        longitude,
    )

    # If birth time occurs before the day's sunrise, use the
    # previous astronomical day for the sunrise/sunset pair.
    if when < sunrise:
        previous_date = utc_date - timedelta(days=1)

        sunrise = eph.sunrise(
            previous_date,
            latitude,
            longitude,
        )

        sunset = eph.sunset(
            previous_date,
            latitude,
            longitude,
        )

    # ------------------------------------------------------------------
    # 11. Build ChartContext
    # ------------------------------------------------------------------

    ctx = ChartContext(
        birth_datetime=when,
        latitude=latitude,
        longitude=longitude,
        ascendant_sign_index=asc.sign_index,
        house_signs=houses.house_signs,
        house_lords=houses.house_lords,
        graha_longitudes={
            name: pos.longitude
            for name, pos in grahas_with_houses.items()
        },
        sunrise=sunrise,
        sunset=sunset,
        ashtakavarga_bindus=None,
    )

    # ------------------------------------------------------------------
    # 12. Calculate Upagrahas
    # ------------------------------------------------------------------

    engine = UpagrahaEngine(conventions)

    upagrahas = engine.calculate(ctx)

    # ------------------------------------------------------------------
    # 13. Calculate Vimshottari Mahadashas
    # ------------------------------------------------------------------

    moon_lon = grahas_with_houses["MOON"].longitude

    mahadashas = compute_mahadashas(
        moon_lon,
        when,
    )

    # ------------------------------------------------------------------
    # 14. Return fully resolved Chart
    # ------------------------------------------------------------------

    return Chart(
        birth_datetime=when,
        latitude=latitude,
        longitude=longitude,
        ascendant=asc,
        houses=houses,
        grahas=grahas_with_houses,
        sun_longitude=sun_lon,
        sunrise=sunrise,
        sunset=sunset,
        upagrahas=upagrahas,
        mahadashas=mahadashas,
        conventions=conventions,
    )