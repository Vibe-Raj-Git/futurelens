"""
Career evidence rules.

Seven rules produce typed evidence for the career domain.
"""

from __future__ import annotations

from futurelens.domains.career.definitions import (
    BENEFICS,
    CAREER_HOUSE_REASONS,
    CAREER_HOUSES,
    CAREER_RELEVANT_YOGAS,
    CAREER_SIGNIFICATORS,
    SIGNIFICATOR_REASONS,
    is_dusthana,
    is_kendra,
    is_trikona,
)
from futurelens.domains._weighting import (
    weight_for_dasha,
    weight_for_house_lord,
    weight_for_significator,
    weight_for_transit,
    weight_for_upagraha,
)
from futurelens.evidence.rules.base import make_provenance
from futurelens.grahas.formatting import (
    house_phrase,
    ordinal,
    reason_phrase,
    sign_name,
)
from futurelens.models.evidence import (
    Direction,
    Evidence,
    EvidenceType,
    Weight,
)


DOMAIN = "CAREER"


def _prov(rule_id: str, basis: str, method: str) -> object:
    return make_provenance(
        rule_id=rule_id,
        classical_basis=basis,
        calculation_method=method,
        calculation_convention="WHOLE_SIGN",
    )


def _evaluate_placement(house: int | None, combust: bool) -> tuple[Direction, str]:
    """
    Shared direction logic for career lord and significator placement.

    Rules:
      - in dusthana -> adverse (weakened)
      - combust -> adverse
      - in kendra or trikona -> protective (strong placement)
      - in a career house (10/6/2/11) -> protective (relevant placement)
      - in 1st -> protective (self-related)
      - otherwise -> protective (neutral)
    """
    if house is None:
        return Direction.PROTECTIVE, "neutral_placement"
    if is_dusthana(house):
        return Direction.ADVERSE, "placement_in_dusthana"
    if combust:
        return Direction.ADVERSE, "placement_combust"
    if is_kendra(house) or is_trikona(house):
        return Direction.PROTECTIVE, "placement_in_kendra_or_trikona"
    if house in CAREER_HOUSES:
        return Direction.PROTECTIVE, "placement_in_career_house"
    return Direction.PROTECTIVE, "neutral_placement"


# --- Rule 1: Career lord natal -------------------------------------------

def _count_career_houses_ruled_by(chart, lord_name: str) -> int:
    count = 0
    for h in CAREER_HOUSES:
        if chart.houses.lord_of_house(h) == lord_name:
            count += 1
    return count

def rule_career_lord_natal(chart) -> list[Evidence]:
    """
    CAREER-HOUSE-LORD-NATAL-001

    For each of the 10/6/2/11 houses, evaluate the natal position
    of its lord.
    """
    evidence: list[Evidence] = []

    ashtaka = chart.ashtakavarga()
    house_signs = chart.houses.house_signs

    for house in CAREER_HOUSES:
        lord_name = chart.houses.lord_of_house(house)
        lord = chart.grahas[lord_name]
        lord_house = lord.house
        reason = CAREER_HOUSE_REASONS[house]

        direction, placement_reason = _evaluate_placement(
            lord_house, lord.combust
        )

        rules_other = _count_career_houses_ruled_by(chart, lord_name) > 1
        weight = weight_for_house_lord(
            lord_name=lord_name,
            lord_sign=lord.sign_index,
            lord_house=lord_house,
            lord_combust=lord.combust,
            lord_rules_another_wealth_house=rules_other,
        )

        house_sign = house_signs[house]
        sav_bindus = ashtaka.sav.bindus_by_sign[house_sign]
        sav_label = _sav_strength_label(sav_bindus)

        notes = [
            f"house={house}",
            f"house_reason={reason}",
            f"lord={lord_name}",
            f"lord_house={lord_house}",
            f"lord_sign={lord.sign_index}",
            f"lord_nakshatra={lord.nakshatra.nakshatra_name}",
            f"combust={lord.combust}",
            f"retrograde={lord.retrograde}",
            f"graha={lord_name}",
            f"reason={placement_reason}",
            f"sav_bindus={sav_bindus}",
        ]

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="CAREER-HOUSE-LORD-NATAL-001",
                basis="BPHS ch. 24; Phaladeepika ch. 6",
                method="career_lord_natal_evaluation",
            ),
            subject=f"{ordinal(house)} house lord {lord_name}",
            finding=(
                f"{lord_name} is in {house_phrase(lord_house)}, "
                f"{sign_name(lord.sign_index)}. "
                f"The {ordinal(house)} house falls in "
                f"{sign_name(house_sign)}, which holds {sav_bindus} "
                f"SAV bindus ({sav_label})."
            ),
            interpretation=(
                f"The {ordinal(house)} house relates to {reason}. "
                f"The placement is {reason_phrase(placement_reason)}."
            ),
            notes=tuple(notes),
        ))

    return evidence

def rule_career_significator_natal(chart) -> list[Evidence]:
    """
    CAREER-SIGNIFICATOR-NATAL-001

    For each natural career significator (Sun, Saturn, Mercury,
    Jupiter, Mars), evaluate its natal position.
    """
    evidence: list[Evidence] = []

    for name in CAREER_SIGNIFICATORS:
        graha = chart.grahas[name]
        house = graha.house
        reason = SIGNIFICATOR_REASONS[name]

        direction, placement_reason = _evaluate_placement(
            house, graha.combust
        )

        weight = weight_for_significator(
            graha_name=name,
            graha_sign=graha.sign_index,
            graha_house=house,
            graha_combust=graha.combust,
        )

        notes = [
            f"significator={name}",
            f"graha={name}",
            f"reason_significator={reason}",
            f"house={house}",
            f"sign={graha.sign_index}",
            f"nakshatra={graha.nakshatra.nakshatra_name}",
            f"combust={graha.combust}",
            f"retrograde={graha.retrograde}",
            f"reason={placement_reason}",
        ]

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="CAREER-SIGNIFICATOR-NATAL-001",
                basis="BPHS ch. 24; karaka principles",
                method="career_significator_natal_evaluation",
            ),
            subject=f"{name} as natural significator",
            finding=(
                f"{name} is in {house_phrase(house)}, "
                f"{sign_name(graha.sign_index)}."
            ),
            interpretation=(
                f"{name} signifies {reason}. "
                f"The placement is {reason_phrase(placement_reason)}."
            ),
            notes=tuple(notes),
        ))

    return evidence


# --- Rule 3: Career lord dasha activation --------------------------------

def rule_career_lord_dasha(chart, when) -> list[Evidence]:
    """CAREER-LORD-DASHA-001"""
    career_lords = {chart.houses.lord_of_house(h) for h in CAREER_HOUSES}

    dasha = chart.dasha_at(when)
    md = dasha.mahadasha_lord
    ad = dasha.antardasha_lord

    evidence: list[Evidence] = []

    for level_name, lord in (("MAHADASHA", md), ("ANTARDASHA", ad)):
        if lord in career_lords:
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_DASHA_ACTIVATION,
                direction=Direction.PROTECTIVE,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                weight=weight_for_dasha(),
                provenance=_prov(
                    rule_id="CAREER-LORD-DASHA-001",
                    basis="BPHS ch. 46 (Dasha phala)",
                    method="career_lord_dasha_activation",
                ),
                subject=f"{lord} as {level_name.title()} lord",
                finding=(
                    f"{lord} is currently the {level_name.title()} lord."
                ),
                interpretation=(
                    f"{lord} rules a career house, so this period "
                    f"activates career significations."
                ),
                notes=(
                    f"level={level_name}",
                    f"lord={lord}",
                    f"mahadasha={md}",
                    f"antardasha={ad}",
                ),
            ))

    return evidence


# --- Rule 4: Slow-graha transit through career houses --------------------

def rule_career_significator_transit(chart, when) -> list[Evidence]:
    """CAREER-SIGNIFICATOR-TRANSIT-001"""
    transits = chart.transits_at(when)
    evidence: list[Evidence] = []

    for graha_name in ("JUPITER", "SATURN"):
        pos = transits.positions[graha_name]
        house = pos.house_from_lagna

        if house in CAREER_HOUSES:
            direction = (
                Direction.PROTECTIVE
                if graha_name == "JUPITER"
                else Direction.ADVERSE
            )
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_TRANSIT_TRIGGER,
                direction=direction,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                weight=weight_for_transit(),
                provenance=_prov(
                    rule_id="CAREER-SIGNIFICATOR-TRANSIT-001",
                    basis="Gochara principles for Jupiter and Saturn",
                    method="transit_through_career_house",
                ),
                subject=f"{graha_name} transit",
                finding=(
                    f"{graha_name} is transiting {house_phrase(house)} "
                    f"from the ascendant, and "
                    f"{house_phrase(pos.house_from_moon)} from the Moon."
                ),
                interpretation=(
                    f"This is a {direction.value.lower()} transit effect "
                    f"for the career domain."
                ),
                notes=(
                    f"transit_graha={graha_name}",
                    f"graha={graha_name}",
                    f"house_from_lagna={house}",
                    f"house_from_moon={pos.house_from_moon}",
                    f"sign={pos.graha.sign_index}",
                    f"nakshatra={pos.graha.nakshatra.nakshatra_name}",
                ),
            ))

    return evidence


# --- Rule 5: Upagraha in career house ------------------------------------

def rule_career_upagraha_placement(chart) -> list[Evidence]:
    """CAREER-UPAGRAHA-001"""
    from futurelens.upagraha.definitions import DEFINITIONS

    evidence: list[Evidence] = []

    for name, pos in chart.upagrahas.positions.items():
        if pos.house is None or pos.house not in CAREER_HOUSES:
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
            weight=weight_for_upagraha(),
            provenance=_prov(
                rule_id="CAREER-UPAGRAHA-001",
                basis="Phaladeepika ch. 25",
                method="upagraha_in_career_house",
            ),
            subject=f"Upagraha {name.value}",
            finding=(
                f"{name.value} is placed in {house_phrase(pos.house)}."
            ),
            interpretation=(
                f"This is treated as a "
                f"{direction.value.lower()} modifier for the career "
                f"domain."
            ),
            notes=(
                f"upagraha={name.value}",
                f"house={pos.house}",
                f"house_reason={CAREER_HOUSE_REASONS[pos.house]}",
                f"sign={pos.sign_index}",
            ),
        ))

    return evidence


# --- Rule 6: Amala Yoga --------------------------------------------------

def rule_career_amala_yoga(chart) -> list[Evidence]:
    """CAREER-AMALA-YOGA-001"""
    moon_sign = chart.grahas["MOON"].sign_index
    lagna_sign = chart.ascendant.sign_index

    tenth_from_moon = (moon_sign + 9) % 12
    tenth_from_lagna = (lagna_sign + 9) % 12

    evidence: list[Evidence] = []

    for benefic in BENEFICS:
        pos = chart.grahas[benefic]
        sign = pos.sign_index

        if sign == tenth_from_moon:
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
                direction=Direction.PROTECTIVE,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                weight=Weight.STRUCTURAL,
                provenance=_prov(
                    rule_id="CAREER-AMALA-YOGA-001",
                    basis="Phaladeepika ch. 6; Amala Yoga",
                    method="benefic_in_10th_from_moon",
                ),
                subject=f"Amala Yoga ({benefic} from Moon)",
                finding=(
                    f"{benefic} is in the 10th house from the Moon "
                    f"({house_phrase(pos.house)} from the ascendant)."
                ),
                interpretation=(
                    "Amala Yoga grants lasting reputation and "
                    "professional honour."
                ),
                notes=(
                    f"yoga=AMALA",
                    f"graha={benefic}",
                    f"from=MOON",
                    f"sign={sign}",
                    f"house_from_lagna={pos.house}",
                ),
            ))

        if sign == tenth_from_lagna:
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
                direction=Direction.PROTECTIVE,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                weight=Weight.STRUCTURAL,
                provenance=_prov(
                    rule_id="CAREER-AMALA-YOGA-001",
                    basis="Phaladeepika ch. 6; Amala Yoga",
                    method="benefic_in_10th_from_lagna",
                ),
                subject=f"Amala Yoga ({benefic} from Lagna)",
                finding=(
                    f"{benefic} is in the 10th house from the Lagna "
                    f"({house_phrase(pos.house)} from the ascendant)."
                ),
                interpretation=(
                    "Amala Yoga grants lasting reputation and "
                    "professional honour."
                ),
                notes=(
                    f"yoga=AMALA",
                    f"graha={benefic}",
                    f"from=LAGNA",
                    f"sign={sign}",
                    f"house_from_lagna={pos.house}",
                ),
            ))

    return evidence


# --- Rule 7: Career yoga promotion ---------------------------------------

def rule_career_yoga_promotion(chart) -> list[Evidence]:
    """CAREER-YOGA-PROMOTION-001"""
    yoga_report = chart.yogas()

    evidence: list[Evidence] = []

    for yoga_id in CAREER_RELEVANT_YOGAS:
        result = yoga_report.by_id(yoga_id)
        if result is None or not result.present:
            continue

        notes = [
            f"yoga_id={yoga_id}",
            f"yoga_name={result.yoga_name}",
            f"classical_basis={result.classical_basis}",
        ]
        for c in result.conditions_met:
            notes.append(f"condition={c}")

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=Direction.PROTECTIVE,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=Weight.STRUCTURAL,
            provenance=_prov(
                rule_id="CAREER-YOGA-PROMOTION-001",
                basis=result.classical_basis,
                method="career_yoga_promotion",
            ),
            subject=result.yoga_name,
            finding=(
                f"{result.yoga_name} is present in the chart "
                f"(source: {result.classical_basis})."
            ),
            interpretation=(
                "This is a strongly favourable indication for "
                "the career domain."
            ),
            notes=tuple(notes),
        ))

    return evidence


# --- Rule 8: Gochara transit effects -------------------------------------

def rule_career_gochara(chart, when) -> list[Evidence]:
    """
    CAREER-GOCHARA-001

    Filter the four slow-graha Gochara transits to those that affect
    the career houses (10, 6, 2, 11) by occupation or aspect.

    Verdict maps to direction:
      FAVOURABLE verdicts -> PROTECTIVE
      MIXED and UNFAVOURABLE verdicts -> ADVERSE

    Weight:
      STRONG_MODIFIER for STRONGLY_* verdicts
      MODIFIER otherwise
    """
    from futurelens.gochara import compute_gochara
    from futurelens.gochara.engine import GocharaReport
    from futurelens.models.gochara import GocharaVerdict
    from futurelens.models.evidence import Weight

    try:
        report: GocharaReport = compute_gochara(chart, when)
    except Exception:
        return []

    evidence: list[Evidence] = []

    for graha, transit in report.transits.items():
        occupied = transit.house_from_lagna in CAREER_HOUSES
        aspected = any(
            h in CAREER_HOUSES for h in transit.aspected_natal_houses
        )
        if not (occupied or aspected):
            continue

        verdict = transit.final_verdict

        if verdict in (
            GocharaVerdict.STRONGLY_FAVOURABLE,
            GocharaVerdict.FAVOURABLE,
        ):
            direction = Direction.PROTECTIVE
        else:
            direction = Direction.ADVERSE

        if verdict in (
            GocharaVerdict.STRONGLY_FAVOURABLE,
            GocharaVerdict.STRONGLY_UNFAVOURABLE,
        ):
            weight = Weight.STRONG_MODIFIER
        else:
            weight = weight_for_transit()

        relevance_parts = []
        if occupied:
            relevance_parts.append(
                f"occupies house {transit.house_from_lagna}"
            )
        if aspected:
            career_aspects = [
                h for h in transit.aspected_natal_houses
                if h in CAREER_HOUSES
            ]
            relevance_parts.append(
                f"aspects career houses {career_aspects}"
            )
        relevance = " and ".join(relevance_parts)

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_TRANSIT_TRIGGER,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="CAREER-GOCHARA-001",
                basis="Phaladeepika ch. 26; BPHS ch. 34",
                method="career_gochara_filter",
            ),
            subject=f"{graha.title()} Gochara",
            finding=(
                f"{transit.finding} "
                f"It {relevance}."
            ),
            interpretation=(
                f"{transit.interpretation} "
                f"Verdict for the career domain: "
                f"{verdict.value.replace('_', ' ').lower()}."
            ),
            notes=(
                f"graha={graha}",
                f"transit_sign={transit.transit_sign}",
                f"house_from_lagna={transit.house_from_lagna}",
                f"house_from_moon={transit.house_from_moon}",
                f"sav_bindus={transit.sav_bindus}",
                f"motion={transit.motion.value}",
                f"verdict={verdict.value}",
                f"vedha_active={transit.vedha_active}",
            ),
        ))

    return evidence


def _sav_strength_label(bindus: int) -> str:
    """Convert an SAV bindu count into a strength label."""
    if bindus >= 30:
        return "VERY_STRONG"
    if bindus >= 25:
        return "STRONG"
    if bindus >= 20:
        return "MODERATE"
    if bindus >= 15:
        return "WEAK"
    return "VERY_WEAK"

# --- Rule: D9 reconciliation ---------------------------------------------

def rule_career_d9_reconciliation(chart) -> list[Evidence]:
    """CAREER-D9-RECONCILIATION-001

    Surface the D1/D9 reconciliation for grahas relevant to the
    career domain: career lords (10, 6, 2, 11) and career
    significators.
    """
    from futurelens.domains._weighting import (
        d9_reconciliation_evidence,
    )
    from futurelens.domains.career.definitions import (
        CAREER_HOUSES,
        CAREER_SIGNIFICATORS,
    )
    from futurelens.vargas.reconciliation import reconcile

    reconciliation = reconcile(chart)

    career_lords = {
        chart.houses.lord_of_house(h) for h in CAREER_HOUSES
    }
    relevant = career_lords | set(CAREER_SIGNIFICATORS)

    return d9_reconciliation_evidence(
        reconciliation=reconciliation,
        relevant_grahas=relevant,
        domain=DOMAIN,
        prov_factory=_prov,
        rule_id="CAREER-D9-RECONCILIATION-001",
        basis="BPHS ch. 6 (Navamsa as confirmation)",
        method="career_d9_reconciliation",
    )