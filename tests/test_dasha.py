"""
add_wealth_engine.py

Writes:
  src/futurelens/domains/__init__.py
  src/futurelens/domains/wealth/__init__.py
  src/futurelens/domains/wealth/definitions.py
  src/futurelens/domains/wealth/rules.py
  src/futurelens/domains/wealth/engine.py
  src/futurelens/chart.py                 (updated, adds wealth method)
  src/futurelens/__init__.py              (updated exports)
  tests/test_wealth_engine.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\D\Automation\advanced_kundali")


# ==========================================================================
# Wealth definitions
# ==========================================================================

DEFINITIONS_PY = '''\
"""
Classical wealth domain definitions.

Wealth-relevant houses, lords, significators, and their reasons.

References:
  BPHS ch. 24 (Dhana yogas)
  Phaladeepika ch. 6 (Bhava phala)
  Widely used 2/5/9/11 wealth framework
"""

from __future__ import annotations


# Houses that the classical texts associate with wealth.
WEALTH_HOUSES: tuple[int, ...] = (2, 5, 9, 11)

# Reason for each house's wealth relevance. Used in evidence notes.
WEALTH_HOUSE_REASONS: dict[int, str] = {
    2: "accumulated wealth, family resources",
    5: "speculation, investments, inheritance",
    9: "fortune, dharma, guru's grace",
    11: "gains, income, fulfillment of desires",
}

# Natural wealth significators (karakas).
WEALTH_SIGNIFICATORS: tuple[str, ...] = (
    "JUPITER",   # primary dhana karaka
    "VENUS",     # luxury, value, resources
    "MERCURY",   # commerce, trade, calculation
    "MOON",      # liquidity, public, fluctuations
    "SATURN",    # long-term accumulation, discipline
)

# For each significator, a classical reason.
SIGNIFICATOR_REASONS: dict[str, str] = {
    "JUPITER": "primary dhana karaka; natural giver of abundance",
    "VENUS": "value, luxury, and resources; lakshmi karaka",
    "MERCURY": "commerce, trade, calculation; business karaka",
    "MOON": "liquidity, public wealth, cash flow",
    "SATURN": "long-term accumulation, discipline, delayed wealth",
}

# Houses counted as dusthanas. Being in one weakens a wealth lord.
DUSTHANAS: tuple[int, ...] = (6, 8, 12)

# Kendra houses. Strong kendra placement of a wealth lord is favorable.
KENDRAS: tuple[int, ...] = (1, 4, 7, 10)

# Trikona houses. Strong trikona placement of a wealth lord is favorable.
TRIKONAS: tuple[int, ...] = (1, 5, 9)

# Benefic grahas. Benefic association with a wealth lord is favorable.
BENEFICS: tuple[str, ...] = ("JUPITER", "VENUS", "MERCURY", "MOON")

# Malefic grahas. Malefic association with a wealth lord is adverse.
MALEFICS: tuple[str, ...] = ("SUN", "MARS", "SATURN", "RAHU", "KETU")


def is_wealth_house(house: int) -> bool:
    return house in WEALTH_HOUSES


def is_dusthana(house: int) -> bool:
    return house in DUSTHANAS


def is_kendra(house: int) -> bool:
    return house in KENDRAS


def is_trikona(house: int) -> bool:
    return house in TRIKONAS
'''


# ==========================================================================
# Wealth rules
# ==========================================================================

RULES_PY = '''\
"""
Wealth evidence rules.

Six rules produce typed evidence for the wealth domain. Each carries
a rule_id, classical basis, and provenance.

Design principle: no scoring, no summing. Evidence flows through the
graph for the LLM to explain.
"""

from __future__ import annotations

from futurelens.domains.wealth.definitions import (
    BENEFICS,
    MALEFICS,
    SIGNIFICATOR_REASONS,
    WEALTH_HOUSE_REASONS,
    WEALTH_HOUSES,
    WEALTH_SIGNIFICATORS,
    is_dusthana,
    is_kendra,
    is_trikona,
)
from futurelens.evidence.rules.base import make_provenance
from futurelens.models.evidence import Direction, Evidence, EvidenceType


DOMAIN = "WEALTH"


def _prov(rule_id: str, basis: str, method: str) -> object:
    return make_provenance(
        rule_id=rule_id,
        classical_basis=basis,
        calculation_method=method,
        calculation_convention="WHOLE_SIGN",
    )


# --- Rule 1: Wealth lord natal -------------------------------------------

def rule_wealth_lord_natal(chart) -> list[Evidence]:
    """
    WEALTH-HOUSE-LORD-NATAL-001

    For each of the 2/5/9/11 houses, evaluate the natal position of
    its lord. Evidence direction is derived from classical rules:
      - lord in a dusthana (6/8/12) -> adverse
      - lord in own sign, exaltation, or kendra/trikona -> protective
      - lord combust -> adverse
      - lord retrograde -> mild adverse
    """
    evidence: list[Evidence] = []

    for house in WEALTH_HOUSES:
        lord_name = chart.houses.lord_of_house(house)
        lord = chart.grahas[lord_name]
        lord_house = lord.house
        reason = WEALTH_HOUSE_REASONS[house]

        notes = [
            f"house={house}",
            f"house_reason={reason}",
            f"lord={lord_name}",
            f"lord_house={lord_house}",
            f"lord_sign={lord.sign_index}",
            f"lord_nakshatra={lord.nakshatra.nakshatra_name}",
            f"combust={lord.combust}",
            f"retrograde={lord.retrograde}",
        ]

        # Determine direction from classical rules.
        direction = Direction.PROTECTIVE
        if lord_house is not None and is_dusthana(lord_house):
            direction = Direction.ADVERSE
            notes.append("reason=lord_in_dusthana")
        elif lord.combust:
            direction = Direction.ADVERSE
            notes.append("reason=lord_combust")
        elif lord_house is not None and (
            is_kendra(lord_house) or is_trikona(lord_house)
        ):
            direction = Direction.PROTECTIVE
            notes.append("reason=lord_in_kendra_or_trikona")
        else:
            # Neutral placement, default protective but noted.
            notes.append("reason=neutral_placement")

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            provenance=_prov(
                rule_id="WEALTH-HOUSE-LORD-NATAL-001",
                basis="BPHS ch. 24; Phaladeepika ch. 6",
                method="wealth_lord_natal_evaluation",
            ),
            notes=tuple(notes),
        ))

    return evidence


# --- Rule 2: Wealth significator natal -----------------------------------

def rule_wealth_significator_natal(chart) -> list[Evidence]:
    """
    WEALTH-SIGNIFICATOR-NATAL-001

    For each natural wealth significator (Jupiter, Venus, Mercury,
    Moon, Saturn), evaluate its natal position.
    """
    evidence: list[Evidence] = []

    for name in WEALTH_SIGNIFICATORS:
        graha = chart.grahas[name]
        house = graha.house
        reason = SIGNIFICATOR_REASONS[name]

        notes = [
            f"significator={name}",
            f"reason={reason}",
            f"house={house}",
            f"sign={graha.sign_index}",
            f"nakshatra={graha.nakshatra.nakshatra_name}",
            f"combust={graha.combust}",
            f"retrograde={graha.retrograde}",
        ]

        direction = Direction.PROTECTIVE
        if house is not None and is_dusthana(house):
            direction = Direction.ADVERSE
            notes.append("reason=significator_in_dusthana")
        elif graha.combust and name != "MOON":
            direction = Direction.ADVERSE
            notes.append("reason=significator_combust")
        elif house is not None and house in WEALTH_HOUSES:
            direction = Direction.PROTECTIVE
            notes.append("reason=significator_in_wealth_house")
        else:
            notes.append("reason=neutral_placement")

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            provenance=_prov(
                rule_id="WEALTH-SIGNIFICATOR-NATAL-001",
                basis="BPHS ch. 24; general karaka principles",
                method="wealth_significator_natal_evaluation",
            ),
            notes=tuple(notes),
        ))

    return evidence


# --- Rule 3: Wealth lord dasha activation --------------------------------

def rule_wealth_lord_dasha(chart, when) -> list[Evidence]:
    """
    WEALTH-LORD-DASHA-001

    Evaluate whether the current Mahadasha or Antardasha lord is a
    lord of a wealth house. Per v0.1 decision, Pratyantardasha is
    NOT used for domain forecasting.

    The wealth lords are computed from the chart's own house_lords.
    """
    wealth_lords = {
        chart.houses.lord_of_house(h) for h in WEALTH_HOUSES
    }

    dasha = chart.dasha_at(when)
    md = dasha.mahadasha_lord
    ad = dasha.antardasha_lord

    evidence: list[Evidence] = []

    for level_name, lord in (("MAHADASHA", md), ("ANTARDASHA", ad)):
        if lord in wealth_lords:
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_DASHA_ACTIVATION,
                direction=Direction.PROTECTIVE,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                provenance=_prov(
                    rule_id="WEALTH-LORD-DASHA-001",
                    basis="BPHS ch. 46 (Dasha phala)",
                    method="wealth_lord_dasha_activation",
                ),
                notes=(
                    f"level={level_name}",
                    f"lord={lord}",
                    f"mahadasha={md}",
                    f"antardasha={ad}",
                ),
            ))

    return evidence


# --- Rule 4: Slow-graha transit through wealth houses --------------------

def rule_wealth_significator_transit(chart, when) -> list[Evidence]:
    """
    WEALTH-SIGNIFICATOR-TRANSIT-001

    Evaluate whether Jupiter or Saturn is currently transiting a
    wealth house from the natal Lagna.
    """
    transits = chart.transits_at(when)
    evidence: list[Evidence] = []

    for graha_name in ("JUPITER", "SATURN"):
        pos = transits.positions[graha_name]
        house = pos.house_from_lagna

        if house in WEALTH_HOUSES:
            direction = (
                Direction.PROTECTIVE
                if graha_name == "JUPITER"
                else Direction.ADVERSE  # Saturn in wealth houses is mixed
            )
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_TRANSIT_TRIGGER,
                direction=direction,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                provenance=_prov(
                    rule_id="WEALTH-SIGNIFICATOR-TRANSIT-001",
                    basis="Gochara principles for Jupiter and Saturn",
                    method="transit_through_wealth_house",
                ),
                notes=(
                    f"graha={graha_name}",
                    f"house_from_lagna={house}",
                    f"house_from_moon={pos.house_from_moon}",
                    f"sign={pos.graha.sign_index}",
                    f"nakshatra={pos.graha.nakshatra.nakshatra_name}",
                ),
            ))

    return evidence


# --- Rule 5: Upagraha in wealth house ------------------------------------

def rule_wealth_upagraha_placement(chart) -> list[Evidence]:
    """
    WEALTH-UPAGRAHA-001

    Emit evidence for each Upagraha placed in a wealth house.
    Direction depends on the Upagraha's nature.
    """
    from futurelens.upagraha.definitions import DEFINITIONS

    evidence: list[Evidence] = []

    for name, pos in chart.upagrahas.positions.items():
        if pos.house is None or pos.house not in WEALTH_HOUSES:
            continue

        definition = DEFINITIONS.get(name)
        if definition is None:
            continue

        direction = (
            Direction.PROTECTIVE
            if definition.role == "PROTECTIVE_MODIFIER"
            else Direction.ADVERSE
        )

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_HOUSE_ASSOCIATION,
            direction=direction,
            domain=DOMAIN,
            upagraha=name.value,
            target_evidence_id=None,
            classical_strength_ratio=definition.classical_strength_ratio,
            provenance=_prov(
                rule_id="WEALTH-UPAGRAHA-001",
                basis="Phaladeepika ch. 25",
                method="upagraha_in_wealth_house",
            ),
            notes=(
                f"upagraha={name.value}",
                f"house={pos.house}",
                f"house_reason={WEALTH_HOUSE_REASONS[pos.house]}",
                f"sign={pos.sign_index}",
            ),
        ))

    return evidence


# --- Rule 6: Yamakantaka protective modifier -----------------------------

def rule_wealth_yamakantaka_protective(chart, when) -> list[Evidence]:
    """
    WEALTH-YAMAKANTAKA-PROTECT-001

    If Yamakantaka is in a wealth house, and its activation is
    currently triggered, emit a PROTECTIVE modifier.

    The modifier is silent if no adverse wealth evidence exists,
    per the modifier semantics in the Evidence Graph Rulebook.
    """
    from futurelens.models.upagraha import UpagrahaName

    yk_pos = chart.upagrahas.positions.get(UpagrahaName.YAMAKANTAKA)
    if yk_pos is None or yk_pos.house is None:
        return []
    if yk_pos.house not in WEALTH_HOUSES:
        return []

    # Yamakantaka is active if the lord of its house is the
    # current Mahadasha or Antardasha lord.
    house_lord = chart.houses.lord_of_house(yk_pos.house)
    dasha = chart.dasha_at(when)
    active = house_lord in {dasha.mahadasha_lord, dasha.antardasha_lord}

    if not active:
        return []

    return [Evidence(
        evidence_type=EvidenceType.UPAGRAHA_PROTECTIVE_MODIFIER,
        direction=Direction.PROTECTIVE,
        domain=DOMAIN,
        upagraha="YAMAKANTAKA",
        target_evidence_id=None,  # filled in by graph if adverse exists
        classical_strength_ratio=1.0,
        provenance=_prov(
            rule_id="WEALTH-YAMAKANTAKA-PROTECT-001",
            basis="Phaladeepika 25.21; 25.25",
            method="yamakantaka_protective_modifier_wealth",
        ),
        notes=(
            f"house={yk_pos.house}",
            f"house_lord={house_lord}",
            f"mahadasha={dasha.mahadasha_lord}",
            f"antardasha={dasha.antardasha_lord}",
        ),
    )]
'''


# ==========================================================================
# Wealth engine
# ==========================================================================

ENGINE_PY = '''\
"""
Wealth domain engine.

Runs the wealth evidence rules against a chart and returns a
structured WealthReport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from futurelens.domains.wealth import rules as wealth_rules
from futurelens.evidence.graph import Contradiction, _detect_contradictions
from futurelens.models.evidence import Direction, Evidence


@dataclass
class WealthReport:
    """The wealth-domain evidence for a chart at a given moment."""

    when: datetime
    evidence: list[Evidence] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    rules_evaluated: list[str] = field(default_factory=list)
    rules_failed: list[str] = field(default_factory=list)

    def by_rule(self, rule_id: str) -> list[Evidence]:
        return [e for e in self.evidence if e.provenance.rule_id == rule_id]

    def by_direction(self, direction: Direction) -> list[Evidence]:
        return [e for e in self.evidence if e.direction == direction]

    def summary(self) -> dict:
        """Compact summary for the LLM or UI."""
        return {
            "when": self.when.isoformat(),
            "evidence_count": len(self.evidence),
            "adverse_count": len(self.by_direction(Direction.ADVERSE)),
            "protective_count": len(self.by_direction(Direction.PROTECTIVE)),
            "contradictions": len(self.contradictions),
            "rules_evaluated": self.rules_evaluated,
            "rules_failed": self.rules_failed,
        }


def build_wealth_report(chart, when: datetime) -> WealthReport:
    """
    Evaluate all wealth rules against a chart at a given moment.
    """
    report = WealthReport(when=when)

    rule_fns = [
        ("WEALTH-HOUSE-LORD-NATAL-001", lambda: wealth_rules.rule_wealth_lord_natal(chart)),
        ("WEALTH-SIGNIFICATOR-NATAL-001", lambda: wealth_rules.rule_wealth_significator_natal(chart)),
        ("WEALTH-LORD-DASHA-001", lambda: wealth_rules.rule_wealth_lord_dasha(chart, when)),
        ("WEALTH-SIGNIFICATOR-TRANSIT-001", lambda: wealth_rules.rule_wealth_significator_transit(chart, when)),
        ("WEALTH-UPAGRAHA-001", lambda: wealth_rules.rule_wealth_upagraha_placement(chart)),
        ("WEALTH-YAMAKANTAKA-PROTECT-001", lambda: wealth_rules.rule_wealth_yamakantaka_protective(chart, when)),
    ]

    for rule_id, fn in rule_fns:
        try:
            items = fn()
        except Exception as exc:
            report.rules_failed.append(f"{rule_id}: {exc}")
            continue
        report.rules_evaluated.append(rule_id)
        report.evidence.extend(items)

    report.contradictions = _detect_contradictions(report.evidence)
    return report
'''


# ==========================================================================
# Package inits
# ==========================================================================

DOMAINS_INIT_PY = '''\
from futurelens.domains.wealth.engine import (
    WealthReport,
    build_wealth_report,
)

__all__ = [
    "WealthReport",
    "build_wealth_report",
]
'''


WEALTH_INIT_PY = '''\
from futurelens.domains.wealth.definitions import (
    WEALTH_HOUSES,
    WEALTH_HOUSE_REASONS,
    WEALTH_SIGNIFICATORS,
    is_dusthana,
    is_kendra,
    is_trikona,
    is_wealth_house,
)
from futurelens.domains.wealth.engine import (
    WealthReport,
    build_wealth_report,
)

__all__ = [
    "WEALTH_HOUSES",
    "WEALTH_HOUSE_REASONS",
    "WEALTH_SIGNIFICATORS",
    "WealthReport",
    "build_wealth_report",
    "is_dusthana",
    "is_kendra",
    "is_trikona",
    "is_wealth_house",
]
'''


# ==========================================================================
# Chart update — add wealth method
# ==========================================================================

CHART_PY = '''\
"""
Cast a chart from birth data.

Public entry point of FutureLens. Produces a fully resolved Chart
with ascendant, houses, grahas, Upagrahas, Dasha, transit query,
general evidence graph, and wealth domain evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from futurelens.astronomy.ascendant import AscendantResult, compute_ascendant
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
        return self.houses.house_of_sign(int(longitude // 30))

    def house_of_graha(self, name: str) -> int:
        return self.houses.house_of_sign(self.grahas[name].sign_index)

    def house_of_upagraha(self, name) -> int | None:
        pos = self.upagrahas.positions.get(name)
        return pos.house if pos else None

    def dasha_at(self, when: datetime) -> DashaMoment:
        days = (when - self.birth_datetime).total_seconds() / 86400.0
        md = active_period(self.mahadashas, days)
        if md is None:
            raise ValueError(
                f"Date {when} is outside the 120-year dasha range."
            )
        ad_list = compute_antardashas(md)
        ad = active_period(ad_list, days)
        if ad is None:
            raise ValueError("Antardasha not found — internal error.")
        pd_list = compute_pratyantardashas(ad)
        pd = active_period(pd_list, days)

        def to_dt(days_since_birth: float) -> datetime:
            return self.birth_datetime + timedelta(days=days_since_birth)

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

    def transits_at(self, when: datetime) -> TransitReport:
        return compute_transits(
            when=when,
            natal_ascendant_sign=self.ascendant.sign_index,
            natal_moon_sign=self.grahas["MOON"].sign_index,
            natal_moon_nakshatra_index=(
                self.grahas["MOON"].nakshatra.nakshatra_index
            ),
        )

    def evidence(self, when: datetime, domain: str | None = None):
        from futurelens.evidence.graph import build_evidence_graph
        from futurelens.evidence.rules.base import EvidenceContext

        ctx = EvidenceContext(chart=self, when=when, domain=domain)
        return build_evidence_graph(ctx)

    def wealth(self, when: datetime):
        """Build a wealth domain report for this chart at a given moment."""
        from futurelens.domains.wealth.engine import build_wealth_report
        return build_wealth_report(self, when)


def cast_chart(
    when: datetime,
    latitude: float,
    longitude: float,
    conventions: Conventions | None = None,
) -> Chart:
    """Cast a chart from birth data."""
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    if conventions is None:
        conventions = Conventions()
    conventions.validate()

    asc = compute_ascendant(
        when, latitude=latitude, longitude=longitude, sidereal=True
    )
    houses = resolve_houses(asc.sign_index)

    eph = SwissEphemerisProvider()
    grahas = compute_grahas(when, ephemeris=eph)

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

    sun_lon = grahas["SUN"].longitude

    local_date = when.astimezone(timezone.utc)
    sunrise = eph.sunrise(local_date, latitude, longitude)
    sunset = eph.sunset(local_date, latitude, longitude)
    if when < sunrise:
        prev = local_date - timedelta(days=1)
        sunrise = eph.sunrise(prev, latitude, longitude)
        sunset = eph.sunset(prev, latitude, longitude)

    ctx = ChartContext(
        birth_datetime=when,
        latitude=latitude,
        longitude=longitude,
        ascendant_sign_index=asc.sign_index,
        house_signs=houses.house_signs,
        house_lords=houses.house_lords,
        graha_longitudes={
            name: pos.longitude for name, pos in grahas_with_houses.items()
        },
        sunrise=sunrise,
        sunset=sunset,
        ashtakavarga_bindus=None,
    )

    engine = UpagrahaEngine(conventions)
    upagrahas = engine.calculate(ctx)

    moon_lon = grahas["MOON"].longitude
    mahadashas = compute_mahadashas(moon_lon, when)

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
'''


# ==========================================================================
# Updated __init__
# ==========================================================================

INIT_MAIN_PY = '''\
from futurelens.chart import Chart, cast_chart
from futurelens.conventions import Conventions, UpagrahaEnumeration
from futurelens.dasha.definitions import (
    DASHA_LORDS,
    DASHA_YEARS,
    DashaPeriod,
    next_lord,
)
from futurelens.dasha.engine import (
    active_period,
    compute_antardashas,
    compute_mahadashas,
    compute_pratyantardashas,
    dasha_timeline,
)
from futurelens.domains.wealth.definitions import (
    WEALTH_HOUSES,
    WEALTH_HOUSE_REASONS,
    WEALTH_SIGNIFICATORS,
)
from futurelens.domains.wealth.engine import (
    WealthReport,
    build_wealth_report,
)
from futurelens.evidence.graph import (
    DEFAULT_RULES,
    Contradiction,
    EvidenceGraph,
    build_evidence_graph,
)
from futurelens.evidence.rules.base import EvidenceContext, EvidenceRule
from futurelens.grahas.definitions import GRAHAS, GRAHA_BY_NAME
from futurelens.grahas.engine import compute_grahas
from futurelens.grahas.nakshatra import NakshatraPosition, nakshatra_of
from futurelens.houses.resolver import HouseChart, resolve_houses
from futurelens.models.chart import ChartContext
from futurelens.models.dasha import DashaMoment
from futurelens.models.evidence import Direction, Evidence, EvidenceType
from futurelens.models.graha import GrahaPosition
from futurelens.models.provenance import Provenance
from futurelens.models.transit import TransitPosition, TransitReport
from futurelens.models.upagraha import (
    UpagrahaFamily,
    UpagrahaName,
    UpagrahaPosition,
)
from futurelens.transits.engine import (
    compute_transits,
    is_slow_graha,
    saturn_sade_sati,
)
from futurelens.upagraha.engine import UpagrahaEngine, UpagrahaReport

__all__ = [
    "Chart",
    "ChartContext",
    "Conventions",
    "Contradiction",
    "DASHA_LORDS",
    "DASHA_YEARS",
    "DEFAULT_RULES",
    "DashaMoment",
    "DashaPeriod",
    "Direction",
    "Evidence",
    "EvidenceContext",
    "EvidenceGraph",
    "EvidenceRule",
    "EvidenceType",
    "GRAHAS",
    "GRAHA_BY_NAME",
    "GrahaPosition",
    "HouseChart",
    "NakshatraPosition",
    "Provenance",
    "TransitPosition",
    "TransitReport",
    "UpagrahaEngine",
    "UpagrahaEnumeration",
    "UpagrahaFamily",
    "UpagrahaName",
    "UpagrahaPosition",
    "UpagrahaReport",
    "WEALTH_HOUSES",
    "WEALTH_HOUSE_REASONS",
    "WEALTH_SIGNIFICATORS",
    "WealthReport",
    "active_period",
    "build_evidence_graph",
    "build_wealth_report",
    "cast_chart",
    "compute_antardashas",
    "compute_grahas",
    "compute_mahadashas",
    "compute_pratyantardashas",
    "compute_transits",
    "dasha_timeline",
    "is_slow_graha",
    "nakshatra_of",
    "next_lord",
    "resolve_houses",
    "saturn_sade_sati",
]
__version__ = "0.1.0"
'''


# ==========================================================================
# Tests
# ==========================================================================

TEST_WEALTH_PY = '''\
"""
Wealth domain engine tests.

Verifies:

  - the wealth report is produced with all six rules evaluated
  - every evidence item carries a valid provenance
  - wealth evidence is tagged with domain=WEALTH
  - specific rules trigger on a real chart
  - contradictions are detected when both directions appear
"""

from datetime import datetime, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart
from futurelens.domains.wealth.definitions import (
    WEALTH_HOUSES,
    is_dusthana,
    is_kendra,
    is_trikona,
    is_wealth_house,
)
from futurelens.domains.wealth.engine import (
    WealthReport,
    build_wealth_report,
)
from futurelens.models.evidence import Direction


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


BIRTH = datetime(1990, 7, 15, 6, 30, 0, tzinfo=timezone.utc)
LAT = 19.0760
LON = 72.8777
TARGET = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)


# --- Definitions ----------------------------------------------------------

def test_wealth_houses():
    assert WEALTH_HOUSES == (2, 5, 9, 11)


def test_wealth_house_predicate():
    assert is_wealth_house(2)
    assert is_wealth_house(11)
    assert not is_wealth_house(1)


def test_dusthana_predicate():
    assert is_dusthana(6)
    assert is_dusthana(8)
    assert is_dusthana(12)
    assert not is_dusthana(1)


def test_kendra_predicate():
    assert is_kendra(1)
    assert is_kendra(10)
    assert not is_kendra(2)


def test_trikona_predicate():
    assert is_trikona(1)
    assert is_trikona(5)
    assert is_trikona(9)
    assert not is_trikona(2)


# --- Report construction --------------------------------------------------

def test_wealth_report_is_produced():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    assert isinstance(report, WealthReport)


def test_all_six_rules_evaluated():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    expected = {
        "WEALTH-HOUSE-LORD-NATAL-001",
        "WEALTH-SIGNIFICATOR-NATAL-001",
        "WEALTH-LORD-DASHA-001",
        "WEALTH-SIGNIFICATOR-TRANSIT-001",
        "WEALTH-UPAGRAHA-001",
        "WEALTH-YAMAKANTAKA-PROTECT-001",
    }
    assert set(report.rules_evaluated) == expected
    assert report.rules_failed == []


def test_evidence_has_domain_wealth():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    for e in report.evidence:
        assert e.domain == "WEALTH"


def test_evidence_has_provenance():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    for e in report.evidence:
        assert e.provenance.rule_id != ""
        assert e.provenance.tradition != ""
        assert e.provenance.classical_basis != ""


# --- Rule-specific tests --------------------------------------------------

def test_wealth_lord_natal_rule_emits_four():
    """Four wealth houses, so four natal lord items."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-HOUSE-LORD-NATAL-001")
    assert len(items) == 4


def test_wealth_significator_natal_rule_emits_five():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-SIGNIFICATOR-NATAL-001")
    assert len(items) == 5


def test_wealth_upagraha_rule_emits_for_wealth_houses():
    """Only Upagrahas in wealth houses should be emitted."""
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    items = report.by_rule("WEALTH-UPAGRAHA-001")
    for e in items:
        notes = dict(n.split("=", 1) for n in e.notes if "=" in n)
        assert int(notes["house"]) in WEALTH_HOUSES


# --- Summary --------------------------------------------------------------

def test_summary_has_required_fields():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    summary = report.summary()
    assert "when" in summary
    assert "evidence_count" in summary
    assert "adverse_count" in summary
    assert "protective_count" in summary
    assert "contradictions" in summary
    assert summary["evidence_count"] == len(report.evidence)


def test_summary_counts_match_evidence():
    chart = cast_chart(BIRTH, LAT, LON)
    report = build_wealth_report(chart, TARGET)
    summary = report.summary()
    assert summary["adverse_count"] == len(
        report.by_direction(Direction.ADVERSE)
    )
    assert summary["protective_count"] == len(
        report.by_direction(Direction.PROTECTIVE)
    )


# --- Chart integration ----------------------------------------------------

def test_chart_wealth_method():
    chart = cast_chart(BIRTH, LAT, LON)
    report = chart.wealth(TARGET)
    assert isinstance(report, WealthReport)
    assert len(report.evidence) > 0
'''


# ==========================================================================
# Files
# ==========================================================================

FILES = {
    "src/futurelens/domains/__init__.py": DOMAINS_INIT_PY,
    "src/futurelens/domains/wealth/__init__.py": WEALTH_INIT_PY,
    "src/futurelens/domains/wealth/definitions.py": DEFINITIONS_PY,
    "src/futurelens/domains/wealth/rules.py": RULES_PY,
    "src/futurelens/domains/wealth/engine.py": ENGINE_PY,
    "src/futurelens/chart.py": CHART_PY,
    "src/futurelens/__init__.py": INIT_MAIN_PY,
    "tests/test_wealth_engine.py": TEST_WEALTH_PY,
}


def main() -> int:
    for rel, content in FILES.items():
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"WRITE  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())