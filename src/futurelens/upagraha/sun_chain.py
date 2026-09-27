from __future__ import annotations

from futurelens.exceptions import InvariantViolation
from futurelens.models.upagraha import (
    UpagrahaFamily,
    UpagrahaName,
    UpagrahaPosition,
)

DHUMA_OFFSET = 133.0 + 20.0 / 60.0
UPAKETU_OFFSET = 16.0 + 40.0 / 60.0


def _normalize(lon: float) -> float:
    return lon % 360.0


def _position(name: UpagrahaName, lon: float) -> UpagrahaPosition:
    lon = _normalize(lon)
    sign_index = int(lon // 30)
    return UpagrahaPosition(
        name=name,
        family=UpagrahaFamily.SUN_DERIVED,
        longitude=lon,
        sign_index=sign_index,
        degree_in_sign=lon - sign_index * 30.0,
    )


def compute_sun_chain(sun_longitude: float) -> dict[UpagrahaName, UpagrahaPosition]:
    """Phaladeepika ch. 25 Sun-derived chain."""
    sun = _normalize(sun_longitude)
    dhuma = _normalize(sun + DHUMA_OFFSET)
    vyatipata = _normalize(360.0 - dhuma)
    parivesha = _normalize(vyatipata + 180.0)
    indrachapa = _normalize(360.0 - parivesha)
    upaketu = _normalize(indrachapa + UPAKETU_OFFSET)
    return {
        UpagrahaName.DHUMA: _position(UpagrahaName.DHUMA, dhuma),
        UpagrahaName.VYATIPATA: _position(UpagrahaName.VYATIPATA, vyatipata),
        UpagrahaName.PARIVESHA: _position(UpagrahaName.PARIVESHA, parivesha),
        UpagrahaName.INDRACHAPA: _position(UpagrahaName.INDRACHAPA, indrachapa),
        UpagrahaName.UPAKETU: _position(UpagrahaName.UPAKETU, upaketu),
    }


def validate_sun_chain(chain: dict[UpagrahaName, UpagrahaPosition]) -> None:
    def angsep(a: float, b: float) -> float:
        d = abs((a - b) % 360.0)
        return min(d, 360.0 - d)

    dhuma = chain[UpagrahaName.DHUMA].longitude
    indrachapa = chain[UpagrahaName.INDRACHAPA].longitude
    vyatipata = chain[UpagrahaName.VYATIPATA].longitude
    parivesha = chain[UpagrahaName.PARIVESHA].longitude

    if abs(angsep(dhuma, indrachapa) - 180.0) > 1e-6:
        raise InvariantViolation("INV-SUN-001: Dhuma / Indrachapa not opposite.")
    if abs(angsep(vyatipata, parivesha) - 180.0) > 1e-6:
        raise InvariantViolation("INV-SUN-002: Vyatipata / Parivesha not opposite.")
