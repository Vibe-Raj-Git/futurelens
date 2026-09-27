"""
Wealth evidence rules.

Seven rules produce typed evidence for the wealth domain. Each
carries a rule_id, classical basis, direction, and weight tier.
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
from futurelens.grahas.formatting import (
    house_phrase,
    ordinal,
    reason_phrase,
    sign_name,
)
from futurelens.domains._weighting import (
    weight_for_dasha,
    weight_for_house_lord,
    weight_for_significator,
    weight_for_transit,
    weight_for_upagraha,
)
from futurelens.models.evidence import Direction, Evidence, EvidenceType, Weight


DOMAIN = "WEALTH"


def _prov(rule_id: str, basis: str, method: str) -> object:
    return make_provenance(
        rule_id=rule_id,
        classical_basis=basis,
        calculation_method=method,
        calculation_convention="WHOLE_SIGN",
    )


def _count_wealth_houses_ruled_by(chart, lord_name: str) -> int:
    """How many wealth houses this lord rules."""
    count = 0
    for h in WEALTH_HOUSES:
        if chart.houses.lord_of_house(h) == lord_name:
            count += 1
    return count


# --- Rule 1: Wealth lord natal -------------------------------------------

def rule_wealth_lord_natal(chart) -> list[Evidence]:
    """
    WEALTH-HOUSE-LORD-NATAL-001

    For each of the 2/5/9/11 houses, evaluate the natal position
    of its lord.
    """
    evidence: list[Evidence] = []

    for house in WEALTH_HOUSES:
        lord_name = chart.houses.lord_of_house(house)
        lord = chart.grahas[lord_name]
        lord_house = lord.house
        reason = WEALTH_HOUSE_REASONS[house]

        direction = Direction.PROTECTIVE
        reason_key = "placement_in_kendra_or_trikona"
        if lord_house is not None and is_dusthana(lord_house):
            direction = Direction.ADVERSE
            reason_key = "placement_in_dusthana"
        elif lord.combust:
            direction = Direction.ADVERSE
            reason_key = "placement_combust"
        elif lord_house in (2, 4, 5, 7, 9, 11):
            reason_key = "placement_in_wealth_house"

        rules_other_wealth_house = _count_wealth_houses_ruled_by(
            chart, lord_name
        ) > 1

        weight = weight_for_house_lord(
            lord_name=lord_name,
            lord_sign=lord.sign_index,
            lord_house=lord_house,
            lord_combust=lord.combust,
            lord_rules_another_wealth_house=rules_other_wealth_house,
        )

        # Semantic fields for the LLM and API consumers.
        _subject = (
            f"{ordinal(house)} house lord {lord_name}"
        )
        _finding_parts = [
            f"{lord_name} is in {house_phrase(lord_house)}, "
            f"{sign_name(lord.sign_index)}."
        ]
        if lord.combust:
            _finding_parts.append(
                f"It is combust, which weakens its significations."
            )
        _finding = " ".join(_finding_parts)

        _interp = (
            f"The {ordinal(house)} house relates to {reason}. "
            f"The placement is {reason_phrase(reason_key)}."
        )

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="WEALTH-HOUSE-LORD-NATAL-001",
                basis="BPHS ch. 24; Phaladeepika ch. 6",
                method="wealth_lord_natal_evaluation",
            ),
            subject=_subject,
            finding=_finding,
            interpretation=_interp,
            notes=(
                f"house={house}",
                f"house_reason={reason}",
                f"lord={lord_name}",
                f"lord_house={lord_house}",
                f"lord_sign={lord.sign_index}",
                f"lord_nakshatra={lord.nakshatra.nakshatra_name}",
                f"combust={lord.combust}",
                f"retrograde={lord.retrograde}",
                f"graha={lord_name}",
                f"reason={reason_key}",
            ),
        ))

    return evidence


# --- Rule 2: Wealth significator natal -----------------------------------

def rule_wealth_significator_natal(chart) -> list[Evidence]:
    """WEALTH-SIGNIFICATOR-NATAL-001"""
    evidence: list[Evidence] = []

    for name in WEALTH_SIGNIFICATORS:
        graha = chart.grahas[name]
        house = graha.house
        reason = SIGNIFICATOR_REASONS[name]

        direction = Direction.PROTECTIVE
        reason_key = "placement_in_kendra_or_trikona"
        if house is not None and is_dusthana(house):
            direction = Direction.ADVERSE
            reason_key = "placement_in_dusthana"
        elif graha.combust and name != "MOON":
            direction = Direction.ADVERSE
            reason_key = "placement_combust"

        weight = weight_for_significator(
            graha_name=name,
            graha_sign=graha.sign_index,
            graha_house=house,
            graha_combust=graha.combust,
        )

        _subject = f"{name} as natural significator"
        _finding = (
            f"{name} is in {house_phrase(house)}, "
            f"{sign_name(graha.sign_index)}."
        )
        if graha.combust and name != "MOON":
            _finding += " It is combust, which weakens its effect."
        _interp = (
            f"{name} signifies {reason}. "
            f"The placement is {reason_phrase(reason_key)}."
        )

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="WEALTH-SIGNIFICATOR-NATAL-001",
                basis="BPHS ch. 24; karaka principles",
                method="wealth_significator_natal_evaluation",
            ),
            subject=_subject,
            finding=_finding,
            interpretation=_interp,
            notes=(
                f"significator={name}",
                f"graha={name}",
                f"reason_significator={reason}",
                f"house={house}",
                f"sign={graha.sign_index}",
                f"nakshatra={graha.nakshatra.nakshatra_name}",
                f"combust={graha.combust}",
                f"retrograde={graha.retrograde}",
                f"reason={reason_key}",
            ),
        ))

    return evidence


# --- Rule 3: Wealth lord dasha activation --------------------------------

def rule_wealth_lord_dasha(chart, when) -> list[Evidence]:
    """WEALTH-LORD-DASHA-001"""
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
                weight=weight_for_dasha(),
                provenance=_prov(
                    rule_id="WEALTH-LORD-DASHA-001",
                    basis="BPHS ch. 46 (Dasha phala)",
                    method="wealth_lord_dasha_activation",
                ),
                subject=f"{lord} as {level_name.title()} lord",
                finding=(
                    f"{lord} is currently the {level_name.title()} lord."
                ),
                interpretation=(
                    f"{lord} rules a wealth house, so this period "
                    f"activates wealth significations."
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
    """WEALTH-SIGNIFICATOR-TRANSIT-001"""
    transits = chart.transits_at(when)
    evidence: list[Evidence] = []

    for graha_name in ("JUPITER", "SATURN"):
        pos = transits.positions[graha_name]
        house = pos.house_from_lagna
        if house in WEALTH_HOUSES:
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
                    rule_id="WEALTH-SIGNIFICATOR-TRANSIT-001",
                    basis="Gochara principles for Jupiter and Saturn",
                    method="transit_through_wealth_house",
                ),
                subject=f"{graha_name} transit",
                finding=(
                    f"{graha_name} is transiting {house_phrase(house)} "
                    f"from the ascendant, and "
                    f"{house_phrase(pos.house_from_moon)} from the Moon."
                ),
                interpretation=(
                    f"This is a {direction.value.lower()} transit effect "
                    f"for the wealth domain."
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


# --- Rule 5: Upagraha in wealth house ------------------------------------

def rule_wealth_upagraha_placement(chart) -> list[Evidence]:
    """WEALTH-UPAGRAHA-001"""
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
            weight=weight_for_upagraha(),
            provenance=_prov(
                rule_id="WEALTH-UPAGRAHA-001",
                basis="Phaladeepika ch. 25",
                method="upagraha_in_wealth_house",
            ),
            subject=f"Upagraha {name.value}",
            finding=(
                f"{name.value} is placed in {house_phrase(pos.house)}."
            ),
            interpretation=(
                f"This is treated as a "
                f"{direction.value.lower()} modifier for the wealth "
                f"domain."
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
    """WEALTH-YAMAKANTAKA-PROTECT-001"""
    from futurelens.models.upagraha import UpagrahaName

    yk_pos = chart.upagrahas.positions.get(UpagrahaName.YAMAKANTAKA)
    if yk_pos is None or yk_pos.house is None:
        return []
    if yk_pos.house not in WEALTH_HOUSES:
        return []

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
        target_evidence_id=None,
        classical_strength_ratio=1.0,
        weight=weight_for_upagraha(),
        provenance=_prov(
            rule_id="WEALTH-YAMAKANTAKA-PROTECT-001",
            basis="Phaladeepika 25.21; 25.25",
            method="yamakantaka_protective_modifier_wealth",
        ),
        subject="Yamakantaka protective effect",
        finding=(
            f"Yamakantaka is in {house_phrase(yk_pos.house)}, and its "
            f"activating lord {house_lord} is currently in dasha."
        ),
        interpretation=(
            "Yamakantaka provides a protective influence for wealth "
            "during this period."
        ),
        notes=(
            f"upagraha=YAMAKANTAKA",
            f"house={yk_pos.house}",
            f"house_lord={house_lord}",
            f"mahadasha={dasha.mahadasha_lord}",
            f"antardasha={dasha.antardasha_lord}",
        ),
    )]


# --- Rule 7: Wealth yoga promotion ---------------------------------------

def rule_wealth_yoga_promotion(chart) -> list[Evidence]:
    """WEALTH-YOGA-PROMOTION-001"""
    from futurelens.domains.wealth.definitions import (
        WEALTH_RELEVANT_YOGAS,
    )

    yoga_report = chart.yogas()
    evidence: list[Evidence] = []

    for yoga_id in WEALTH_RELEVANT_YOGAS:
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
                rule_id="WEALTH-YOGA-PROMOTION-001",
                basis=result.classical_basis,
                method="wealth_yoga_promotion",
            ),
            subject=result.yoga_name,
            finding=(
                f"{result.yoga_name} is present in the chart "
                f"(source: {result.classical_basis})."
            ),
            interpretation=(
                "This is a strongly favourable indication for the "
                "wealth domain."
            ),
            notes=tuple(notes),
        ))
    return evidence


# --- Rule 8: Gochara transit effects -------------------------------------

def rule_wealth_gochara(chart, when) -> list[Evidence]:
    """
    WEALTH-GOCHARA-001

    Filter the four slow-graha Gochara transits to those that affect
    the wealth houses (2, 5, 9, 11) by occupation or by aspect.

    Verdict maps to direction:
      STRONGLY_FAVOURABLE, FAVOURABLE -> PROTECTIVE
      STRONGLY_UNFAVOURABLE, UNFAVOURABLE -> ADVERSE
      MIXED -> ADVERSE (mixed is treated as a caution)

    Weight:
      STRONG_MODIFIER for the STRONGLY_* verdicts
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
        # Does the transit occupy or aspect a wealth house?
        occupied = transit.house_from_lagna in WEALTH_HOUSES
        aspected = any(
            h in WEALTH_HOUSES for h in transit.aspected_natal_houses
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
            wealth_aspects = [
                h for h in transit.aspected_natal_houses
                if h in WEALTH_HOUSES
            ]
            relevance_parts.append(
                f"aspects wealth houses {wealth_aspects}"
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
                rule_id="WEALTH-GOCHARA-001",
                basis="Phaladeepika ch. 26; BPHS ch. 34",
                method="wealth_gochara_filter",
            ),
            subject=f"{graha.title()} Gochara",
            finding=(
                f"{transit.finding} "
                f"It {relevance}."
            ),
            interpretation=(
                f"{transit.interpretation} "
                f"Verdict for the wealth domain: "
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
