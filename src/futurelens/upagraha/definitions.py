from __future__ import annotations

from dataclasses import dataclass

from futurelens.conventions import UpagrahaEnumeration
from futurelens.models.upagraha import UpagrahaFamily, UpagrahaName


@dataclass(frozen=True)
class UpagrahaDefinition:
    name: UpagrahaName
    family: UpagrahaFamily
    parent_graha: str
    nature: str
    role: str
    classical_strength_ratio: float


DEFINITIONS: dict[UpagrahaName, UpagrahaDefinition] = {
    UpagrahaName.GULIKA: UpagrahaDefinition(
        UpagrahaName.GULIKA, UpagrahaFamily.KALAVELA,
        "SATURN", "MALEFIC", "OBSTRUCTION_MODIFIER", 1.0,
    ),
    UpagrahaName.YAMAKANTAKA: UpagrahaDefinition(
        UpagrahaName.YAMAKANTAKA, UpagrahaFamily.KALAVELA,
        "JUPITER", "BENEFIC", "PROTECTIVE_MODIFIER", 1.0,
    ),
    UpagrahaName.KALA: UpagrahaDefinition(
        UpagrahaName.KALA, UpagrahaFamily.KALAVELA,
        "SUN", "ADVERSE", "LOSS_MODIFIER", 0.5,
    ),
    UpagrahaName.ARDHAPRAHARA: UpagrahaDefinition(
        UpagrahaName.ARDHAPRAHARA, UpagrahaFamily.KALAVELA,
        "MERCURY", "CONTEXT_DEPENDENT", "OBSTACLE_MODIFIER", 0.5,
    ),
    UpagrahaName.MRITYU: UpagrahaDefinition(
        UpagrahaName.MRITYU, UpagrahaFamily.KALAVELA,
        "MARS", "ADVERSE", "SEVERITY_MODIFIER", 0.5,
    ),
    UpagrahaName.DHUMA: UpagrahaDefinition(
        UpagrahaName.DHUMA, UpagrahaFamily.SUN_DERIVED,
        "MARS", "ADVERSE", "DESTRUCTION_MODIFIER", 0.5,
    ),
    UpagrahaName.VYATIPATA: UpagrahaDefinition(
        UpagrahaName.VYATIPATA, UpagrahaFamily.SUN_DERIVED,
        "RAHU", "ADVERSE", "CHAOS_MODIFIER", 0.5,
    ),
    UpagrahaName.PARIVESHA: UpagrahaDefinition(
        UpagrahaName.PARIVESHA, UpagrahaFamily.SUN_DERIVED,
        "MOON", "ADVERSE", "ILLUSION_MODIFIER", 0.5,
    ),
    UpagrahaName.INDRACHAPA: UpagrahaDefinition(
        UpagrahaName.INDRACHAPA, UpagrahaFamily.SUN_DERIVED,
        "VENUS", "ADVERSE", "DECEPTION_MODIFIER", 0.5,
    ),
    UpagrahaName.UPAKETU: UpagrahaDefinition(
        UpagrahaName.UPAKETU, UpagrahaFamily.SUN_DERIVED,
        "KETU", "ADVERSE", "ENDING_MODIFIER", 0.5,
    ),
}

KALAVELA_NAMES: tuple[UpagrahaName, ...] = (
    UpagrahaName.GULIKA,
    UpagrahaName.YAMAKANTAKA,
    UpagrahaName.KALA,
    UpagrahaName.ARDHAPRAHARA,
    UpagrahaName.MRITYU,
)

SUN_DERIVED_NAMES: tuple[UpagrahaName, ...] = (
    UpagrahaName.DHUMA,
    UpagrahaName.VYATIPATA,
    UpagrahaName.PARIVESHA,
    UpagrahaName.INDRACHAPA,
    UpagrahaName.UPAKETU,
)


def kalavela_for(enumeration: UpagrahaEnumeration) -> tuple[UpagrahaName, ...]:
    if enumeration == UpagrahaEnumeration.PRIMARY_NINE:
        return (
            UpagrahaName.GULIKA,
            UpagrahaName.YAMAKANTAKA,
            UpagrahaName.KALA,
            UpagrahaName.ARDHAPRAHARA,
        )
    return KALAVELA_NAMES
