"""
Gochara computation engine.

Computes the current transit of the four slow grahas (Jupiter,
Saturn, Rahu, Ketu) relative to a natal chart, applies the classical
favourable/unfavourable tables from the natal Moon and the natal
ascendant, checks Vedha cancellation, reads the SAV bindu support
of the transited sign, casts the transit graha's aspects on the
natal chart, and produces a final Gochara verdict.

The engine consumes a Chart object (already computed) and a target
moment. It produces one GocharaTransit per slow graha.

Reference:
  Phaladeepika ch. 26
  BPHS ch. 34
  Jyotish Sara Sangraha (for Vedha)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from futurelens.gochara.definitions import (
    SLOW_GRAHAS,
    is_favourable_from_lagna,
    is_favourable_from_moon,
    vedha_target_for,
)
from futurelens.grahas.nakshatra import NAKSHATRA_NAMES, nakshatra_of
from futurelens.models.gochara import (
    GocharaMotion,
    GocharaTransit,
    GocharaVerdict,
    SadeSatiPhase,
)
from futurelens.transits.engine import compute_transits


# --------------------------------------------------------------------------
# Aspect offsets for the slow grahas (whole-sign aspects)
# --------------------------------------------------------------------------
# Jupiter: 5th, 7th, 9th from its transited sign
# Saturn:  3rd, 7th, 10th
# Rahu:    5th, 7th, 9th
# Ketu:    5th, 7th, 9th
#
# The values here are sign offsets (1-based) added to the transit
# sign index to obtain the sign that receives the aspect.

ASPECT_OFFSETS: dict[str, tuple[int, ...]] = {
    "JUPITER": (5, 7, 9),
    "SATURN": (3, 7, 10),
    "RAHU": (5, 7, 9),
    "KETU": (5, 7, 9),
}


# --------------------------------------------------------------------------
# Sign names
# --------------------------------------------------------------------------

SIGN_NAMES: tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


# --------------------------------------------------------------------------
# Report type
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GocharaReport:
    """The complete Gochara picture at a moment."""

    when: datetime
    transits: dict[str, GocharaTransit]   # graha -> transit

    def by_graha(self, graha: str) -> GocharaTransit | None:
        return self.transits.get(graha)

    def favourable(self) -> list[GocharaTransit]:
        return [
            t for t in self.transits.values()
            if t.final_verdict in (
                GocharaVerdict.STRONGLY_FAVOURABLE,
                GocharaVerdict.FAVOURABLE,
            )
        ]

    def unfavourable(self) -> list[GocharaTransit]:
        return [
            t for t in self.transits.values()
            if t.final_verdict in (
                GocharaVerdict.UNFAVOURABLE,
                GocharaVerdict.STRONGLY_UNFAVOURABLE,
            )
        ]

    def mixed(self) -> list[GocharaTransit]:
        return [
            t for t in self.transits.values()
            if t.final_verdict == GocharaVerdict.MIXED
        ]


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------

def _house_from_sign(sign: int, reference_sign: int) -> int:
    """Whole-sign house number of `sign` counted from `reference_sign`."""
    return ((sign - reference_sign) % 12) + 1


def _aspect_houses(
    transit_sign: int,
    graha: str,
    ascendant_sign: int,
) -> tuple[int, ...]:
    """
    Return the natal houses aspected by a transiting graha.

    Whole-sign aspects. The transited sign is offset by each
    aspect offset, and the resulting sign is converted to a house
    from the ascendant.
    """
    offsets = ASPECT_OFFSETS.get(graha, (7,))
    houses: list[int] = []
    for offset in offsets:
        aspected_sign = (transit_sign + offset - 1) % 12
        house = _house_from_sign(aspected_sign, ascendant_sign)
        if house not in houses:
            houses.append(house)
    return tuple(sorted(houses))


def _motion_for(graha: str, speed: float) -> GocharaMotion:
    """
    Classify motion state.

    Rahu and Ketu are always retrograde by convention.
    Jupiter and Saturn are classified by the sign of their speed:
      speed < 0     -> RETROGRADE
      |speed| < 0.05 deg/day -> NEAR_STATION
      otherwise     -> DIRECT
    """
    if graha in ("RAHU", "KETU"):
        return GocharaMotion.RETROGRADE
    if speed < 0.0:
        return GocharaMotion.RETROGRADE
    if abs(speed) < 0.05:
        return GocharaMotion.NEAR_STATION
    return GocharaMotion.DIRECT


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


def _sade_sati_phase(
    graha: str,
    transit_nakshatra: int,
    natal_moon_nakshatra: int,
) -> SadeSatiPhase | None:
    """
    Return the Sade Sati phase if Saturn is transiting the 12th,
    1st, or 2nd nakshatra from the natal Moon.
    """
    if graha != "SATURN":
        return None
    distance = (transit_nakshatra - natal_moon_nakshatra) % 27
    if distance == 26:
        return SadeSatiPhase.RISING
    if distance == 0:
        return SadeSatiPhase.PEAK
    if distance == 1:
        return SadeSatiPhase.SETTING
    return None


def _check_vedha(
    graha: str,
    favourable_house_from_moon: int,
    transit_houses_from_moon: dict[str, int],
) -> tuple[bool, str | None, int | None]:
    """
    Check whether Vedha is active for a favourable transit.

    Vedha applies only if the transit house is one of the graha's
    favourable houses AND another slow graha occupies the Vedha
    point.

    Returns (active, blocker_name, blocker_house_from_moon).
    """
    target = vedha_target_for(graha, favourable_house_from_moon)
    if target is None:
        return False, None, None

    for other_name, other_house in transit_houses_from_moon.items():
        if other_name == graha:
            continue
        if other_house == target:
            return True, other_name, other_house

    return False, None, None


def _compute_verdict(
    graha: str,
    base_from_moon: str,
    base_from_lagna: str,
    vedha_active: bool,
    sav_strength: str,
    motion: GocharaMotion,
) -> tuple[GocharaVerdict, str]:
    """
    Compute the final Gochara verdict from the inputs.
    """
    favourable = base_from_moon == "FAVOURABLE"
    strong_sav = sav_strength in ("STRONG", "VERY_STRONG")
    weak_sav = sav_strength in ("WEAK", "VERY_WEAK")

    if favourable and not vedha_active and strong_sav:
        return (
            GocharaVerdict.STRONGLY_FAVOURABLE,
            f"{base_from_moon} transit from Moon, no Vedha, "
            f"SAV {sav_strength.lower()}.",
        )

    if favourable and not vedha_active:
        return (
            GocharaVerdict.FAVOURABLE,
            f"{base_from_moon} transit from Moon, no Vedha.",
        )

    if favourable and vedha_active:
        return (
            GocharaVerdict.MIXED,
            f"{base_from_moon} transit from Moon but Vedha active.",
        )

    if not favourable and strong_sav:
        return (
            GocharaVerdict.MIXED,
            f"{base_from_moon} transit from Moon but SAV support "
            f"({sav_strength.lower()}) partially compensates.",
        )

    if not favourable and weak_sav:
        return (
            GocharaVerdict.STRONGLY_UNFAVOURABLE,
            f"{base_from_moon} transit from Moon and weak SAV support.",
        )

    return (
        GocharaVerdict.UNFAVOURABLE,
        f"{base_from_moon} transit from Moon.",
    )


def _semantic_text(
    graha: str,
    transit_sign_name: str,
    house_from_lagna: int,
    house_from_moon: int,
    sav_bindus: int,
    sav_strength: str,
    base_verdict_from_moon: str,
    vedha_active: bool,
    vedha_by: str | None,
    vedha_house: int | None,
    sade_sati_phase: SadeSatiPhase | None,
    final_verdict: GocharaVerdict,
    aspected_natal_houses: tuple[int, ...],
) -> tuple[str, str, str]:
    """Compose subject, finding, interpretation for the LLM."""
    subject = f"{graha.title()} transit"

    finding_parts = [
        f"{graha.title()} is transiting {transit_sign_name}, "
        f"the {house_from_lagna}th house from the ascendant and "
        f"the {house_from_moon}th house from the Moon."
    ]
    finding_parts.append(
        f"SAV bindus in {transit_sign_name}: {sav_bindus} ({sav_strength})."
    )
    if aspected_natal_houses:
        houses_str = ", ".join(str(h) for h in aspected_natal_houses)
        finding_parts.append(
            f"It aspects natal houses {houses_str}."
        )
    finding = " ".join(finding_parts)

    interp_parts = [
        f"The transit is classified as {final_verdict.value.replace('_', ' ').lower()} "
        f"by classical Gochara."
    ]
    interp_parts.append(
        f"Base verdict from the Moon: {base_verdict_from_moon.lower()}."
    )
    if vedha_active:
        interp_parts.append(
            f"Vedha is active: {vedha_by.title()} occupies the "
            f"{vedha_house}th house from the Moon, blocking the "
            f"favourable effect."
        )
    if sade_sati_phase is not None:
        interp_parts.append(
            f"Sade Sati phase: {sade_sati_phase.value.lower()}."
        )
    interpretation = " ".join(interp_parts)

    return subject, finding, interpretation


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def compute_gochara(
    chart,
    when: datetime,
) -> GocharaReport:
    """
    Compute the Gochara transits of the four slow grahas at a
    given moment relative to the natal chart.

    Parameters
    ----------
    chart : futurelens.chart.Chart
        The natal chart. Provides the ascendant sign, natal Moon
        sign and nakshatra, and the SAV bindus from Ashtakavarga.
    when : datetime
        The moment for which to compute the transits.

    Returns
    -------
    GocharaReport
    """
    # 1. Compute the current transit positions via the existing
    #    transit engine. This handles the ephemeris call.
    transit_report = chart.transits_at(when)

    # 2. Fetch the SAV bindus from Ashtakavarga.
    ashtaka = chart.ashtakavarga()
    sav_bindus_by_sign = ashtaka.sav.bindus_by_sign

    # 3. Natal references.
    natal_ascendant = chart.ascendant.sign_index
    natal_moon_sign = chart.grahas["MOON"].sign_index
    natal_moon_nak = chart.grahas["MOON"].nakshatra.nakshatra_index

    # 4. First pass: collect house-from-moon for every slow graha,
    #    so we can check Vedha across grahas.
    positions: dict[str, dict] = {}
    for graha in SLOW_GRAHAS:
        tp = transit_report.positions[graha]
        sign = tp.graha.sign_index
        house_from_moon = tp.house_from_moon
        positions[graha] = {
            "sign": sign,
            "house_from_moon": house_from_moon,
            "house_from_lagna": tp.house_from_lagna,
            "graha_obj": tp.graha,
            "speed": tp.longitude_speed,
        }

    transit_houses_from_moon = {
        name: p["house_from_moon"] for name, p in positions.items()
    }

    # 5. Second pass: build the GocharaTransit for each graha.
    transits: dict[str, GocharaTransit] = {}

    for graha in SLOW_GRAHAS:
        info = positions[graha]
        sign = info["sign"]
        sign_name = SIGN_NAMES[sign]
        house_from_lagna = info["house_from_lagna"]
        house_from_moon = info["house_from_moon"]

        graha_pos = info["graha_obj"]
        graha_pos_speed = info["speed"]
        nak_index = graha_pos.nakshatra.nakshatra_index
        nak_name = graha_pos.nakshatra.nakshatra_name
        nak_from_moon = (nak_index - natal_moon_nak) % 27

        sav = sav_bindus_by_sign[sign]
        sav_strength = _sav_strength_label(sav)

        motion = _motion_for(graha, graha_pos_speed)

        base_moon = (
            "FAVOURABLE"
            if is_favourable_from_moon(graha, house_from_moon)
            else "UNFAVOURABLE"
        )
        base_lagna = (
            "FAVOURABLE"
            if is_favourable_from_lagna(graha, house_from_lagna)
            else "UNFAVOURABLE"
        )

        vedha_active = False
        vedha_by = None
        vedha_house = None
        if base_moon == "FAVOURABLE":
            active, blocker, blocker_house = _check_vedha(
                graha, house_from_moon, transit_houses_from_moon
            )
            vedha_active = active
            vedha_by = blocker
            vedha_house = blocker_house

        aspected_houses = _aspect_houses(
            sign, graha, natal_ascendant
        )

        sade_sati = _sade_sati_phase(
            graha, nak_index, natal_moon_nak
        )

        final_verdict, reason = _compute_verdict(
            graha=graha,
            base_from_moon=base_moon,
            base_from_lagna=base_lagna,
            vedha_active=vedha_active,
            sav_strength=sav_strength,
            motion=motion,
        )

        subject, finding, interpretation = _semantic_text(
            graha=graha,
            transit_sign_name=sign_name,
            house_from_lagna=house_from_lagna,
            house_from_moon=house_from_moon,
            sav_bindus=sav,
            sav_strength=sav_strength,
            base_verdict_from_moon=base_moon,
            vedha_active=vedha_active,
            vedha_by=vedha_by,
            vedha_house=vedha_house,
            sade_sati_phase=sade_sati,
            final_verdict=final_verdict,
            aspected_natal_houses=aspected_houses,
        )

        transits[graha] = GocharaTransit(
            graha=graha,
            when=when,
            transit_sign=sign,
            transit_sign_name=sign_name,
            transit_longitude=graha_pos.longitude,
            house_from_lagna=house_from_lagna,
            house_from_moon=house_from_moon,
            transit_nakshatra=nak_index,
            transit_nakshatra_name=nak_name,
            nakshatra_from_moon=nak_from_moon,
            sav_bindus=sav,
            sav_strength=sav_strength,
            motion=motion,
            base_verdict_from_moon=base_moon,
            base_verdict_from_lagna=base_lagna,
            vedha_active=vedha_active,
            vedha_by=vedha_by,
            vedha_house=vedha_house,
            aspected_natal_houses=aspected_houses,
            sade_sati_phase=sade_sati,
            final_verdict=final_verdict,
            verdict_reason=reason,
            subject=subject,
            finding=finding,
            interpretation=interpretation,
        )

    return GocharaReport(when=when, transits=transits)
