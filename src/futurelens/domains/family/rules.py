"""
FAMILY evidence rules.

Eight rules produce typed evidence for the FAMILY domain. Each
carries a rule_id, classical basis, direction, and weight tier.
"""

from __future__ import annotations

from futurelens.domains._weighting import (
    weight_for_dasha,
    weight_for_house_lord,
    weight_for_significator,
    weight_for_transit,
    weight_for_upagraha,
)
from futurelens.domains.family.definitions import (
    FAMILY_HOUSE_REASONS,
    FAMILY_HOUSES,
    FAMILY_RELATIONSHIPS,
    FAMILY_RELEVANT_YOGAS,
    SIGNIFICATOR_REASONS,
    is_dusthana,
)
from futurelens.evidence.rules.base import make_provenance
from futurelens.grahas.formatting import (
    house_phrase,
    ordinal,
    reason_phrase,
    sign_name,
    verdict_phrase,
)
from futurelens.grahas.dignity import (
    is_debilitated,
    is_exalted,
    is_moolatrikona,
    is_own_sign,
)
from futurelens.models.evidence import Direction, Evidence, EvidenceType, Weight


DOMAIN = "FAMILY"


def _prov(rule_id: str, basis: str, method: str) -> object:
    return make_provenance(
        rule_id=rule_id,
        classical_basis=basis,
        calculation_method=method,
        calculation_convention="WHOLE_SIGN",
    )


def _count_family_houses_ruled_by(chart, lord_name: str) -> int:
    count = 0
    for h in FAMILY_HOUSES:
        if chart.houses.lord_of_house(h) == lord_name:
            count += 1
    return count


# --- Rule 1: Family house lord natal -------------------------------------

def rule_family_lord_natal(chart) -> list[Evidence]:
    """
    FAMILY-HOUSE-LORD-NATAL-001

    For each of the six family houses (2, 4, 5, 7, 9, 12),
    evaluate the natal position of its lord.
    """
    evidence: list[Evidence] = []

    ashtaka = chart.ashtakavarga()
    house_signs = chart.houses.house_signs

    for house in FAMILY_HOUSES:
        lord_name = chart.houses.lord_of_house(house)
        lord = chart.grahas[lord_name]
        lord_house = lord.house
        reason = FAMILY_HOUSE_REASONS[house]

        direction = Direction.PROTECTIVE
        reason_key = "placement_in_kendra_or_trikona"
        if lord_house is not None and is_dusthana(lord_house):
            direction = Direction.ADVERSE
            reason_key = "placement_in_dusthana"
        elif lord.combust:
            direction = Direction.ADVERSE
            reason_key = "placement_combust"
        elif lord_house in (2, 4, 5, 7, 9, 12):
            reason_key = "placement_in_family_house"

        rules_other = _count_family_houses_ruled_by(chart, lord_name) > 1

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

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="FAMILY-HOUSE-LORD-NATAL-001",
                basis="BPHS ch. 24; Phaladeepika ch. 6",
                method="family_lord_natal_evaluation",
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
                f"The placement is {reason_phrase(reason_key)}."
            ),
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
                f"sav_bindus={sav_bindus}",
            ),
        ))

    return evidence

def rule_family_significator_natal(chart) -> list[Evidence]:
    """
    FAMILY-SIGNIFICATOR-NATAL-001

    For each of the seven natural family significators, evaluate
    its natal position.
    """
    evidence: list[Evidence] = []

    for name in ("MOON", "SUN", "MARS", "JUPITER", "VENUS", "MERCURY", "SATURN"):
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

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="FAMILY-SIGNIFICATOR-NATAL-001",
                basis="BPHS ch. 24; karaka principles",
                method="family_significator_natal_evaluation",
            ),
            subject=f"{name} as family significator",
            finding=(
                f"{name} is in {house_phrase(house)}, "
                f"{sign_name(graha.sign_index)}."
            ),
            interpretation=(
                f"{name} signifies {reason}. "
                f"The placement is {reason_phrase(reason_key)}."
            ),
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


# --- Rule 3: Specific relationship analysis ------------------------------

def _component_score(
    graha_name: str,
    graha_sign: int,
    graha_house: int | None,
    graha_combust: bool,
) -> int:
    """
    Score a single graha's contribution to a relationship from
    -2 (severely weak) to +2 (strongly favourable).

    Dimensions:
      - debilitation (severe penalty)
      - own/exalted/moolatrikona (strong bonus)
      - favourable vs dusthana house placement
      - combustion status
    """
    strong_sign = (
        is_own_sign(graha_name, graha_sign)
        or is_exalted(graha_name, graha_sign)
        or is_moolatrikona(graha_name, graha_sign)
    )
    weak_sign = is_debilitated(graha_name, graha_sign)
    in_dusthana = graha_house is not None and is_dusthana(graha_house)
    in_favourable = (
        graha_house is not None
        and graha_house in (1, 2, 4, 5, 7, 9, 10, 11)
    )

    # Debilitation dominates; even a good house only partially
    # compensates.
    if weak_sign:
        if in_dusthana:
            return -2
        if in_favourable:
            return 0
        return -1

    if in_dusthana and graha_combust:
        return -2
    if in_dusthana:
        return 0 if strong_sign else -1
    if graha_combust:
        return -1
    if strong_sign and in_favourable:
        return 2
    if strong_sign or in_favourable:
        return 1
    return 0


def rule_family_relationship(chart) -> list[Evidence]:
    """
    FAMILY-RELATIONSHIP-001

    Evaluates each named family relationship (mother, father,
    spouse, children, siblings) using a combined score of the
    relevant house lord and natural significator.

    Both components contribute an independent strength score
    (-2 to +2). Their sum determines the direction and weight:

      >= +2   PROTECTIVE, STRUCTURAL
       +1     PROTECTIVE, SUPPORTING
        0     PROTECTIVE, MODIFIER    (mixed, slight lean)
       -1     ADVERSE, SUPPORTING     (mixed, slight lean)
      <= -2   ADVERSE, STRUCTURAL
    """
    evidence: list[Evidence] = []

    for rel in FAMILY_RELATIONSHIPS:
        name = rel["name"]
        house = rel["house"]
        sig_name = rel["significator"]

        lord_name = chart.houses.lord_of_house(house)
        lord = chart.grahas[lord_name]
        sig = chart.grahas[sig_name]

        lord_score = _component_score(
            lord_name, lord.sign_index, lord.house, lord.combust
        )
        sig_score = _component_score(
            sig_name, sig.sign_index, sig.house, sig.combust
        )
        combined = lord_score + sig_score

        if combined >= 2:
            direction = Direction.PROTECTIVE
            weight = Weight.STRUCTURAL
            verdict = "strongly_supported"
        elif combined == 1:
            direction = Direction.PROTECTIVE
            weight = Weight.SUPPORTING
            verdict = "supported"
        elif combined == 0:
            direction = Direction.PROTECTIVE
            weight = Weight.MODIFIER
            verdict = "mixed_slight_positive"
        elif combined == -1:
            direction = Direction.ADVERSE
            weight = Weight.SUPPORTING
            verdict = "mixed_slight_negative"
        else:
            direction = Direction.ADVERSE
            weight = Weight.STRUCTURAL
            verdict = "challenging"

        _subject = f"{name.title()} relationship"
        _finding = (
            f"The {ordinal(house)} house lord is {lord_name} "
            f"(in {house_phrase(lord.house)}). "
            f"The significator is {sig_name} "
            f"(in {house_phrase(sig.house)})."
        )
        _interp = (
            f"This relationship is {verdict_phrase(verdict)}."
        )

        evidence.append(Evidence(
            evidence_type=EvidenceType.FAMILY_RELATIONSHIP,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="FAMILY-RELATIONSHIP-001",
                basis="BPHS ch. 24; Saravali ch. 30",
                method=f"family_relationship_{name}",
            ),
            subject=_subject,
            finding=_finding,
            interpretation=_interp,
            notes=(
                f"relationship={name}",
                f"house={house}",
                f"house_lord={lord_name}",
                f"lord_house={lord.house}",
                f"lord_score={lord_score}",
                f"significator={sig_name}",
                f"significator_house={sig.house}",
                f"significator_score={sig_score}",
                f"combined_score={combined}",
                f"verdict={verdict}",
            ),
        ))

    return evidence


# --- Rule 4: Family lord dasha activation --------------------------------

def rule_family_lord_dasha(chart, when) -> list[Evidence]:
    """
    FAMILY-LORD-DASHA-001

    Current Mahadasha or Antardasha lord is a lord of a family
    house or a natural family significator.
    """
    family_lords = {
        chart.houses.lord_of_house(h) for h in FAMILY_HOUSES
    }
    family_significators = {
        "MOON", "SUN", "MARS", "JUPITER", "VENUS", "MERCURY", "SATURN"
    }
    relevant = family_lords | family_significators

    dasha = chart.dasha_at(when)
    md = dasha.mahadasha_lord
    ad = dasha.antardasha_lord

    evidence: list[Evidence] = []
    for level_name, lord in (("MAHADASHA", md), ("ANTARDASHA", ad)):
        if lord in relevant:
            evidence.append(Evidence(
                evidence_type=EvidenceType.UPAGRAHA_DASHA_ACTIVATION,
                direction=Direction.PROTECTIVE,
                domain=DOMAIN,
                upagraha=None,
                target_evidence_id=None,
                classical_strength_ratio=1.0,
                weight=weight_for_dasha(),
                provenance=_prov(
                    rule_id="FAMILY-LORD-DASHA-001",
                    basis="BPHS ch. 46 (Dasha phala)",
                    method="family_lord_dasha_activation",
                ),
                subject=f"{lord} as {level_name.title()} lord",
                finding=(
                    f"{lord} is currently the {level_name.title()} lord."
                ),
                interpretation=(
                    f"{lord} is relevant to family significations, so "
                    f"this period activates family matters."
                ),
                notes=(
                    f"level={level_name}",
                    f"lord={lord}",
                    f"is_family_lord={lord in family_lords}",
                    f"is_significator={lord in family_significators}",
                    f"mahadasha={md}",
                    f"antardasha={ad}",
                ),
            ))
    return evidence


# --- Rule 5: Slow-graha transit through family houses --------------------

def rule_family_significator_transit(chart, when) -> list[Evidence]:
    """
    FAMILY-SIGNIFICATOR-TRANSIT-001

    Jupiter or Saturn currently transiting a family house.
    """
    transits = chart.transits_at(when)
    evidence: list[Evidence] = []

    for graha_name in ("JUPITER", "SATURN"):
        pos = transits.positions[graha_name]
        house = pos.house_from_lagna
        if house in FAMILY_HOUSES:
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
                    rule_id="FAMILY-SIGNIFICATOR-TRANSIT-001",
                    basis="Gochara principles for Jupiter and Saturn",
                    method="transit_through_family_house",
                ),
                subject=f"{graha_name} transit",
                finding=(
                    f"{graha_name} is transiting {house_phrase(house)} "
                    f"from the ascendant, and "
                    f"{house_phrase(pos.house_from_moon)} from the Moon."
                ),
                interpretation=(
                    f"This is a {direction.value.lower()} transit effect "
                    f"for the family domain."
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


# --- Rule 6: Upagraha in family house ------------------------------------

def rule_family_upagraha_placement(chart) -> list[Evidence]:
    """
    FAMILY-UPAGRAHA-001

    Each Upagraha placed in a family house.
    """
    from futurelens.upagraha.definitions import DEFINITIONS

    evidence: list[Evidence] = []
    for name, pos in chart.upagrahas.positions.items():
        if pos.house is None or pos.house not in FAMILY_HOUSES:
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
                rule_id="FAMILY-UPAGRAHA-001",
                basis="Phaladeepika ch. 25",
                method="upagraha_in_family_house",
            ),
            subject=f"Upagraha {name.value}",
            finding=(
                f"{name.value} is placed in {house_phrase(pos.house)}."
            ),
            interpretation=(
                f"This is treated as a "
                f"{direction.value.lower()} modifier for the family "
                f"domain."
            ),
            notes=(
                f"upagraha={name.value}",
                f"house={pos.house}",
                f"house_reason={FAMILY_HOUSE_REASONS[pos.house]}",
                f"sign={pos.sign_index}",
            ),
        ))
    return evidence


# --- Rule 7: Yamakantaka protective modifier -----------------------------

def rule_family_yamakantaka_protective(chart, when) -> list[Evidence]:
    """
    FAMILY-YAMAKANTAKA-PROTECT-001
    """
    from futurelens.models.upagraha import UpagrahaName

    yk_pos = chart.upagrahas.positions.get(UpagrahaName.YAMAKANTAKA)
    if yk_pos is None or yk_pos.house is None:
        return []
    if yk_pos.house not in FAMILY_HOUSES:
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
            rule_id="FAMILY-YAMAKANTAKA-PROTECT-001",
            basis="Phaladeepika 25.21; 25.25",
            method="yamakantaka_protective_modifier_family",
        ),
        subject="Yamakantaka protective effect",
        finding=(
            f"Yamakantaka is in {house_phrase(yk_pos.house)}, and its "
            f"activating lord {house_lord} is currently in dasha."
        ),
        interpretation=(
            "Yamakantaka provides a protective influence for family "
            "matters during this period."
        ),
        notes=(
            f"upagraha=YAMAKANTAKA",
            f"house={yk_pos.house}",
            f"house_lord={house_lord}",
            f"mahadasha={dasha.mahadasha_lord}",
            f"antardasha={dasha.antardasha_lord}",
        ),
    )]


# --- Rule 8: Family yoga promotion ---------------------------------------

def rule_family_yoga_promotion(chart) -> list[Evidence]:
    """
    FAMILY-YOGA-PROMOTION-001

    Promotes family-relevant yogas into family evidence.
    """
    yoga_report = chart.yogas()
    evidence: list[Evidence] = []

    for yoga_id in FAMILY_RELEVANT_YOGAS:
        result = yoga_report.by_id(yoga_id)
        if result is None or not result.present:
            continue

        # Chandra-Mangala and Gaja Kesari are protective.
        # Kemadruma is adverse.
        if yoga_id == "KEMADRUMA":
            direction = Direction.ADVERSE
        else:
            direction = Direction.PROTECTIVE

        notes = [
            f"yoga_id={yoga_id}",
            f"yoga_name={result.yoga_name}",
            f"classical_basis={result.classical_basis}",
        ]
        for c in result.conditions_met:
            notes.append(f"condition={c}")

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=Weight.STRUCTURAL,
            provenance=_prov(
                rule_id="FAMILY-YOGA-PROMOTION-001",
                basis=result.classical_basis,
                method="family_yoga_promotion",
            ),
            subject=result.yoga_name,
            finding=(
                f"{result.yoga_name} is present in the chart "
                f"(source: {result.classical_basis})."
            ),
            interpretation=(
                f"This is a strongly "
                f"{'favourable' if direction == Direction.PROTECTIVE else 'challenging'} "
                f"indication for the family domain."
            ),
            notes=tuple(notes),
        ))
    return evidence


# --- Rule 9: Gochara transit effects -------------------------------------

def rule_family_gochara(chart, when) -> list[Evidence]:
    """
    FAMILY-GOCHARA-001

    Filter the four slow-graha Gochara transits to those that affect
    the family houses (2, 4, 5, 7, 9, 12) by occupation or aspect.

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
        occupied = transit.house_from_lagna in FAMILY_HOUSES
        aspected = any(
            h in FAMILY_HOUSES for h in transit.aspected_natal_houses
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
            family_aspects = [
                h for h in transit.aspected_natal_houses
                if h in FAMILY_HOUSES
            ]
            relevance_parts.append(
                f"aspects family houses {family_aspects}"
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
                rule_id="FAMILY-GOCHARA-001",
                basis="Phaladeepika ch. 26; BPHS ch. 34",
                method="family_gochara_filter",
            ),
            subject=f"{graha.title()} Gochara",
            finding=(
                f"{transit.finding} "
                f"It {relevance}."
            ),
            interpretation=(
                f"{transit.interpretation} "
                f"Verdict for the family domain: "
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

