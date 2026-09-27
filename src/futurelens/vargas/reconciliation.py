"""
D1 vs D9 reconciliation.

The D9 chart is a confirmation chart. For each graha, compare its
D1 dignity to its D9 dignity:

  CONFIRMED  - strong in D1 and strong in D9, OR
               weak in D1 and weak in D9
  UPGRADED   - weak in D1, strong in D9
               (Neecha Bhanga at the divisional level)
  DOWNGRADED - strong in D1, weak in D9
  NEUTRAL    - any other combination

Dignity bands:
  strong  = EXALTED, MOOLATRIKONA, OWN_SIGN
  weak    = DEBILITATED
  neutral = everything else (currently NEUTRAL)

Weight tier for evidence:
  CONFIRMED  -> SUPPORTING
  NEUTRAL    -> SUPPORTING
  UPGRADED   -> MODIFIER
  DOWNGRADED -> MODIFIER
"""

from __future__ import annotations

from futurelens.grahas.dignity import dignity_label
from futurelens.models.varga import ReconciliationResult
from futurelens.vargas.navamsa import navamsa_sign_of


_STRONG = frozenset({"EXALTED", "MOOLATRIKONA", "OWN_SIGN"})
_WEAK = frozenset({"DEBILITATED"})


def _band(dignity: str) -> str:
    if dignity in _STRONG:
        return "STRONG"
    if dignity in _WEAK:
        return "WEAK"
    return "NEUTRAL"


def reconcile(chart) -> dict[str, ReconciliationResult]:
    """
    Compare D1 and D9 dignity for every graha in the chart.

    Returns a dict mapping graha name to ReconciliationResult.
    """
    results: dict[str, ReconciliationResult] = {}

    for name, g in chart.grahas.items():
        d1_dignity = dignity_label(name, g.sign_index)
        d9_sign = navamsa_sign_of(g.longitude)
        d9_dignity = dignity_label(name, d9_sign)

        b1 = _band(d1_dignity)
        b9 = _band(d9_dignity)

        if b1 == b9 and b1 in ("STRONG", "WEAK"):
            category = "CONFIRMED"
        elif b1 == "WEAK" and b9 == "STRONG":
            category = "UPGRADED"
        elif b1 == "STRONG" and b9 == "WEAK":
            category = "DOWNGRADED"
        else:
            category = "NEUTRAL"

        weight_tier = (
            "MODIFIER"
            if category in ("UPGRADED", "DOWNGRADED")
            else "SUPPORTING"
        )

        explanation = _explain(name, d1_dignity, d9_dignity, category)

        results[name] = ReconciliationResult(
            name=name,
            d1_dignity=d1_dignity,
            d9_dignity=d9_dignity,
            category=category,
            weight_tier=weight_tier,
            explanation=explanation,
        )

    return results


def _explain(name: str, d1: str, d9: str, category: str) -> str:
    if category == "CONFIRMED":
        return (
            f"{name} is {d1.lower()} in D1 and {d9.lower()} in D9. "
            f"The D9 chart confirms the D1 judgment."
        )
    if category == "UPGRADED":
        return (
            f"{name} is {d1.lower()} in D1 but {d9.lower()} in D9. "
            f"The D9 chart upgrades the D1 judgment - Neecha Bhanga "
            f"at the divisional level."
        )
    if category == "DOWNGRADED":
        return (
            f"{name} is {d1.lower()} in D1 but {d9.lower()} in D9. "
            f"The D9 chart downgrades the D1 judgment - the D1 "
            f"strength is not carried into the navamsa."
        )
    return (
        f"{name} is {d1.lower()} in D1 and {d9.lower()} in D9. "
        f"D1 and D9 do not align on strength or weakness; the D9 "
        f"chart neither confirms nor denies the D1 judgment."
    )