"""
Gochara transit model.

Represents one slow graha's current transit relative to the natal
chart, with the classical Gochara verdict.

The model is frozen and carries no logic. The engine computes; the
model stores.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GocharaMotion(str, Enum):
    """Motion state of a transiting slow graha."""
    DIRECT = "DIRECT"
    RETROGRADE = "RETROGRADE"
    NEAR_STATION = "NEAR_STATION"


class GocharaVerdict(str, Enum):
    """
    The final Gochara verdict for a slow graha transit.

    STRONGLY_FAVOURABLE - favourable base, no Vedha, strong SAV
    FAVOURABLE          - favourable base, no Vedha, moderate/weak SAV
    MIXED               - favourable base blocked by Vedha, OR
                          unfavourable base compensated by strong SAV
    UNFAVOURABLE        - unfavourable base, no compensating SAV
    STRONGLY_UNFAVOURABLE - unfavourable base, weak SAV, adverse motion
    """
    STRONGLY_FAVOURABLE = "STRONGLY_FAVOURABLE"
    FAVOURABLE = "FAVOURABLE"
    MIXED = "MIXED"
    UNFAVOURABLE = "UNFAVOURABLE"
    STRONGLY_UNFAVOURABLE = "STRONGLY_UNFAVOURABLE"


class SadeSatiPhase(str, Enum):
    """The three phases of Saturn's Sade Sati."""
    RISING = "RISING"     # Saturn in the 12th nakshatra from Moon
    PEAK = "PEAK"         # Saturn in the same nakshatra as Moon
    SETTING = "SETTING"   # Saturn in the 2nd nakshatra from Moon


@dataclass(frozen=True)
class GocharaTransit:
    """
    The Gochara transit of one slow graha.

    Attributes are all facts about the transit plus the computed
    verdict. Interpretation belongs to the domain engines.
    """

    # --- Identification ---------------------------------------------------
    graha: str                              # JUPITER, SATURN, RAHU, KETU
    when: datetime                          # the moment of the transit

    # --- Position ---------------------------------------------------------
    transit_sign: int                       # 0..11
    transit_sign_name: str                  # "Cancer"
    transit_longitude: float                # 0..360

    # --- Houses -----------------------------------------------------------
    house_from_lagna: int                   # 1..12
    house_from_moon: int                    # 1..12

    # --- Nakshatra --------------------------------------------------------
    transit_nakshatra: int                  # 0..26
    transit_nakshatra_name: str
    nakshatra_from_moon: int                # 0..26

    # --- SAV bindu support ------------------------------------------------
    sav_bindus: int                         # 0..56
    sav_strength: str                       # VERY_STRONG .. VERY_WEAK

    # --- Motion -----------------------------------------------------------
    motion: GocharaMotion

    # --- Base verdicts ----------------------------------------------------
    base_verdict_from_moon: str             # FAVOURABLE or UNFAVOURABLE
    base_verdict_from_lagna: str            # FAVOURABLE or UNFAVOURABLE

    # --- Vedha ------------------------------------------------------------
    vedha_active: bool
    vedha_by: str | None                    # graha name, or None
    vedha_house: int | None                 # house where the blocker sits

    # --- Aspects on the natal chart ---------------------------------------
    aspected_natal_houses: tuple[int, ...]

    # --- Sade Sati --------------------------------------------------------
    sade_sati_phase: SadeSatiPhase | None

    # --- Final verdict ----------------------------------------------------
    final_verdict: GocharaVerdict
    verdict_reason: str

    # --- Semantic fields for the LLM --------------------------------------
    subject: str = ""
    finding: str = ""
    interpretation: str = ""
