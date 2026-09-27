"""
D9 domain reconciliation tests.

Verifies that the D1/D9 reconciliation (see futurelens.vargas.
reconciliation) surfaces as evidence in each domain engine, filtered
to domain-relevant grahas, with the correct direction and weight
tier per category.

Three fixtures:

  REFERENCE      - Ujjain 1984. CONFIRMED and NEUTRAL cases only.
  UPGRADED_CHART - Delhi 1950-04-05 20:00 IST. Moon is UPGRADED.
  DOWNGRADED_CHART - Delhi 1950-04-25 20:00 IST. Moon is DOWNGRADED.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

try:
    import swisseph  # type: ignore
    HAS_SWE = True
except ImportError:
    HAS_SWE = False

from futurelens.chart import cast_chart


pytestmark = pytest.mark.skipif(
    not HAS_SWE, reason="pyswisseph not installed."
)


_IST = timezone(timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------

def _reference_chart():
    """Ujjain 1984. Scorpio lagna. CONFIRMED (Sun) and NEUTRAL."""
    birth = (
        datetime(1984, 8, 30, 12, 2, 0, tzinfo=_IST)
        .astimezone(timezone.utc)
    )
    return cast_chart(birth, 22.7196, 75.8577)


def _upgraded_chart():
    """Delhi 1950-04-05 20:00 IST. Moon: debilitated D1, own sign D9."""
    birth = (
        datetime(1950, 4, 5, 20, 0, 0, tzinfo=_IST)
        .astimezone(timezone.utc)
    )
    return cast_chart(birth, 28.6139, 77.2090)


def _downgraded_chart():
    """Delhi 1950-04-25 20:00 IST. Moon: own sign D1, debilitated D9."""
    birth = (
        datetime(1950, 4, 25, 20, 0, 0, tzinfo=_IST)
        .astimezone(timezone.utc)
    )
    return cast_chart(birth, 28.6139, 77.2090)


# ---------------------------------------------------------------
# Expected weight/direction per category
# ---------------------------------------------------------------

CATEGORY_TO_WEIGHT = {
    "CONFIRMED": "SUPPORTING",
    "UPGRADED": "MODIFIER",
    "DOWNGRADED": "MODIFIER",
    "NEUTRAL": "SUPPORTING",
}

CATEGORY_TO_DIRECTION = {
    "CONFIRMED": "PROTECTIVE",
    "UPGRADED": "PROTECTIVE",
    "DOWNGRADED": "ADVERSE",
    "NEUTRAL": "PROTECTIVE",
}

DOMAIN_RULE_IDS = {
    "wealth": "WEALTH-D9-RECONCILIATION-001",
    "career": "CAREER-D9-RECONCILIATION-001",
    "family": "FAMILY-D9-RECONCILIATION-001",
}


# =====================================================================
# 1. Rule registration and evidence shape
# =====================================================================

@pytest.mark.parametrize("domain", ["wealth", "career", "family"])
def test_d9_reconciliation_rule_runs(domain):
    """The D9 reconciliation rule must be evaluated in every domain."""
    chart = _reference_chart()
    when = datetime.now(timezone.utc)

    if domain == "wealth":
        report = chart.wealth(when)
    elif domain == "career":
        report = chart.career(when)
    else:
        from futurelens.domains.family.engine import build_family_report
        report = build_family_report(chart, when)

    rule_id = DOMAIN_RULE_IDS[domain]
    assert rule_id in report.rules_evaluated, (
        f"{rule_id} not in rules_evaluated: {report.rules_evaluated}"
    )
    assert rule_id not in report.rules_failed, (
        f"{rule_id} failed: {report.rules_failed}"
    )
    assert len(report.by_rule(rule_id)) > 0, (
        f"{rule_id} produced no evidence"
    )


@pytest.mark.parametrize("domain", ["wealth", "career", "family"])
def test_d9_reconciliation_evidence_shape(domain):
    """Every reconciliation evidence item has the expected fields."""
    chart = _reference_chart()
    when = datetime.now(timezone.utc)

    if domain == "wealth":
        report = chart.wealth(when)
    elif domain == "career":
        report = chart.career(when)
    else:
        from futurelens.domains.family.engine import build_family_report
        report = build_family_report(chart, when)

    rule_id = DOMAIN_RULE_IDS[domain]
    items = report.by_rule(rule_id)
    assert len(items) > 0, f"{rule_id} produced no evidence"
    for e in items:
        # Weight tier is one of the two expected values.
        assert e.weight.value in ("SUPPORTING", "MODIFIER"), (
            f"{e.subject}: unexpected weight {e.weight.value}"
        )
        # Direction is PROTECTIVE or ADVERSE.
        assert e.direction.value in ("PROTECTIVE", "ADVERSE"), (
            f"{e.subject}: unexpected direction {e.direction.value}"
        )
        # Notes must include the category.
        notes = dict(
            pair.split("=", 1)
            for pair in (e.notes or ())
            if "=" in pair
        )
        assert "category" in notes, f"{e.subject}: no category in notes"
        assert notes["category"] in (
            "CONFIRMED", "UPGRADED", "DOWNGRADED", "NEUTRAL"
        ), f"{e.subject}: bad category {notes['category']}"
        # Weight and direction must match the category mapping.
        cat = notes["category"]
        assert e.weight.value == CATEGORY_TO_WEIGHT[cat], (
            f"{e.subject}: weight {e.weight.value} does not match "
            f"category {cat}"
        )
        assert e.direction.value == CATEGORY_TO_DIRECTION[cat], (
            f"{e.subject}: direction {e.direction.value} does not "
            f"match category {cat}"
        )


# =====================================================================
# 2. Domain filtering: only relevant grahas appear
# =====================================================================

def test_wealth_d9_reconciliation_only_relevant_grahas():
    """Wealth reconciliation emits only for wealth lords and significators."""
    chart = _reference_chart()
    when = datetime.now(timezone.utc)
    report = chart.wealth(when)

    rule_id = DOMAIN_RULE_IDS["wealth"]
    subjects = {e.subject for e in report.by_rule(rule_id)}

    # Extract graha names from subjects (format: "<GRAHA> D1/D9 ...").
    grahas_present = {
        s.split()[0] for s in subjects if s
    }

    # Wealth relevant: Jupiter, Venus, Mercury, Moon, Saturn on the
    # reference chart (wealth lords 2/5/9/11 = Jupiter, Moon, Mercury
    # plus significators Venus, Saturn).
    expected = {"JUPITER", "MOON", "MERCURY", "VENUS", "SATURN"}
    # Sun, Mars, Rahu, Ketu are NOT wealth relevant on this chart.
    not_expected = {"SUN", "MARS", "RAHU", "KETU"}

    assert grahas_present == expected, (
        f"wealth D9 grahas mismatch: "
        f"missing={expected - grahas_present}, "
        f"unexpected={grahas_present - expected}"
    )
    for g in not_expected:
        assert g not in grahas_present, (
            f"{g} should not appear in wealth D9 evidence"
        )


def test_career_d9_reconciliation_only_relevant_grahas():
    """Career reconciliation emits only for career lords and significators."""
    chart = _reference_chart()
    when = datetime.now(timezone.utc)
    report = chart.career(when)

    rule_id = DOMAIN_RULE_IDS["career"]
    subjects = {e.subject for e in report.by_rule(rule_id)}
    grahas_present = {s.split()[0] for s in subjects if s}

    # Career significators: SUN, SATURN, MERCURY, JUPITER, MARS.
    # Career lords 10/6/2/11 on Scorpio lagna: SUN (10), MARS (6),
    # JUPITER (2), MERCURY (11).
    expected = {"SUN", "MARS", "MERCURY", "JUPITER", "SATURN"}
    not_expected = {"MOON", "VENUS", "RAHU", "KETU"}

    assert grahas_present == expected, (
        f"career D9 grahas mismatch: "
        f"missing={expected - grahas_present}, "
        f"unexpected={grahas_present - expected}"
    )
    for g in not_expected:
        assert g not in grahas_present, (
            f"{g} should not appear in career D9 evidence"
        )


def test_family_d9_reconciliation_only_relevant_grahas():
    """Family reconciliation emits only for family lords and significators."""
    chart = _reference_chart()
    when = datetime.now(timezone.utc)

    from futurelens.domains.family.engine import build_family_report
    report = build_family_report(chart, when)

    rule_id = DOMAIN_RULE_IDS["family"]
    subjects = {e.subject for e in report.by_rule(rule_id)}
    grahas_present = {s.split()[0] for s in subjects if s}

    # Family significators: MOON, SUN, MARS, JUPITER, VENUS, MERCURY,
    # SATURN. Rahu/Ketu excluded.
    expected = {
        "SUN", "MOON", "MARS", "MERCURY",
        "JUPITER", "VENUS", "SATURN",
    }
    not_expected = {"RAHU", "KETU"}

    assert grahas_present == expected, (
        f"family D9 grahas mismatch: "
        f"missing={expected - grahas_present}, "
        f"unexpected={grahas_present - expected}"
    )
    for g in not_expected:
        assert g not in grahas_present, (
            f"{g} should not appear in family D9 evidence"
        )


# =====================================================================
# 3. UPGRADED and DOWNGRADED cases
# =====================================================================

def test_upgraded_chart_produces_upgraded_evidence():
    """
    On the Delhi 1950-04-05 chart, Moon is debilitated in D1 and in
    its own sign in D9. Every domain where Moon is relevant must
    produce an UPGRADED evidence item for Moon.
    """
    chart = _upgraded_chart()
    when = datetime.now(timezone.utc)

    # Moon is relevant to wealth, career? No - Moon is not a career
    # significator. Moon is relevant to family.
    wealth = chart.wealth(when)
    from futurelens.domains.family.engine import build_family_report
    family = build_family_report(chart, when)

    wealth_items = [
        e for e in wealth.by_rule(DOMAIN_RULE_IDS["wealth"])
        if e.subject.startswith("MOON ")
    ]
    family_items = [
        e for e in family.by_rule(DOMAIN_RULE_IDS["family"])
        if e.subject.startswith("MOON ")
    ]

    for items, domain in ((wealth_items, "wealth"), (family_items, "family")):
        assert len(items) == 1, (
            f"{domain}: expected exactly one MOON reconciliation, "
            f"got {len(items)}"
        )
        e = items[0]
        notes = dict(
            pair.split("=", 1)
            for pair in (e.notes or ())
            if "=" in pair
        )
        assert notes["category"] == "UPGRADED", (
            f"{domain}: MOON category expected UPGRADED, got "
            f"{notes['category']}"
        )
        assert e.weight.value == "MODIFIER"
        assert e.direction.value == "PROTECTIVE"


def test_downgraded_chart_produces_downgraded_evidence():
    """
    On the Delhi 1950-04-25 chart, Moon is in its own sign in D1 and
    debilitated in D9. Every domain where Moon is relevant must
    produce a DOWNGRADED evidence item for Moon.
    """
    chart = _downgraded_chart()
    when = datetime.now(timezone.utc)

    wealth = chart.wealth(when)
    from futurelens.domains.family.engine import build_family_report
    family = build_family_report(chart, when)

    wealth_items = [
        e for e in wealth.by_rule(DOMAIN_RULE_IDS["wealth"])
        if e.subject.startswith("MOON ")
    ]
    family_items = [
        e for e in family.by_rule(DOMAIN_RULE_IDS["family"])
        if e.subject.startswith("MOON ")
    ]

    for items, domain in ((wealth_items, "wealth"), (family_items, "family")):
        assert len(items) == 1, (
            f"{domain}: expected exactly one MOON reconciliation, "
            f"got {len(items)}"
        )
        e = items[0]
        notes = dict(
            pair.split("=", 1)
            for pair in (e.notes or ())
            if "=" in pair
        )
        assert notes["category"] == "DOWNGRADED", (
            f"{domain}: MOON category expected DOWNGRADED, got "
            f"{notes['category']}"
        )
        assert e.weight.value == "MODIFIER"
        assert e.direction.value == "ADVERSE"