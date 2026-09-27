from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from futurelens.conventions import Conventions
from futurelens.exceptions import ConventionError
from futurelens.models.chart import ChartContext
from futurelens.models.upagraha import UpagrahaName, UpagrahaPosition
from futurelens.upagraha.definitions import kalavela_for
from futurelens.upagraha.kalavela import compute_kalavela
from futurelens.upagraha.sun_chain import compute_sun_chain, validate_sun_chain


@dataclass
class UpagrahaReport:
    tradition: str
    version: str
    positions: dict[UpagrahaName, UpagrahaPosition]
    dependencies: list[str] = field(default_factory=list)
    validation: dict[str, str] = field(default_factory=dict)


class UpagrahaEngine:
    """
    Domain-independent Upagraha calculation engine.

    Produces positions only. Evidence and interpretation are produced
    by separate modules.
    """

    TRADITION = "PHALADEEPIKA"
    VERSION = "0.1"

    def __init__(
        self,
        conventions: Conventions,
        ascendant_func: Callable | None = None,
    ) -> None:
        conventions.validate()
        self._conv = conventions
        self._ascendant_func = ascendant_func

    def _resolve_ascendant_func(self):
        if self._ascendant_func is None:
            from futurelens.astronomy.ascendant import compute_ascendant
            return compute_ascendant
        return self._ascendant_func

    def calculate(self, context: ChartContext) -> UpagrahaReport:
        sun_lon = context.graha_longitudes.get("SUN")
        if sun_lon is None:
            raise ConventionError(
                "ChartContext.graha_longitudes must include SUN."
            )

        sun_chain = compute_sun_chain(sun_lon)
        validate_sun_chain(sun_chain)

        asc_func = self._resolve_ascendant_func()
        kalavela = compute_kalavela(
            birth_datetime=context.birth_datetime,
            sunrise=context.sunrise,
            sunset=context.sunset,
            latitude=context.latitude,
            longitude=context.longitude,
            ascendant_func=asc_func,
        )

        included = kalavela_for(self._conv.upagraha_enumeration)
        kalavela_filtered = {k: v for k, v in kalavela.items() if k in included}

        def with_house(pos: UpagrahaPosition) -> UpagrahaPosition:
            house = None
            for h, sign in context.house_signs.items():
                if sign == pos.sign_index:
                    house = h
                    break
            return UpagrahaPosition(
                name=pos.name,
                family=pos.family,
                longitude=pos.longitude,
                sign_index=pos.sign_index,
                degree_in_sign=pos.degree_in_sign,
                house=house,
            )

        positions: dict[UpagrahaName, UpagrahaPosition] = {}
        for name, pos in {**sun_chain, **kalavela_filtered}.items():
            positions[name] = with_house(pos)

        dependencies: list[str] = []
        if "ARDHAPRAHARA" in {n.value for n in positions}:
            if context.ashtakavarga_bindus is None:
                dependencies.append("ASHTAKAVARGA")

        return UpagrahaReport(
            tradition=self.TRADITION,
            version=self.VERSION,
            positions=positions,
            dependencies=dependencies,
            validation={"sun_chain": "OK"},
        )
