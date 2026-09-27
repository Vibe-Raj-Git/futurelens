from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UpagrahaEnumeration(str, Enum):
    PRIMARY_NINE = "PRIMARY_NINE"
    EXTENDED_KALAVELA = "EXTENDED_KALAVELA"


class Ayanamsha(str, Enum):
    """
    Supported sidereal ayanamsha conventions.

    TRUE_CITRA corresponds to Swiss Ephemeris SIDM_TRUE_CITRA
    (True Chitrapaksha).
    """

    TRUE_CITRA = "TRUE_CITRA"
    LAHIRI = "LAHIRI"


@dataclass(frozen=True)
class Conventions:
    """Frozen set of calculation conventions."""

    ayanamsha: Ayanamsha = Ayanamsha.TRUE_CITRA

    upagraha_enumeration: UpagrahaEnumeration = (
        UpagrahaEnumeration.PRIMARY_NINE
    )

    day_division_count: int = 8
    night_division_count: int = 8

    night_start_reference: str = "FIFTH_WEEKDAY_LORD"
    segment_reference: str = "START_OF_SEGMENT"

    def validate(self) -> None:
        if self.day_division_count != 8:
            raise ValueError(
                "Phaladeepika ch. 25 specifies 8 day divisions."
            )

        if self.night_division_count != 8:
            raise ValueError(
                "Phaladeepika ch. 25 specifies 8 night divisions."
            )