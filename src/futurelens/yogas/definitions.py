"""
Yoga identifiers and metadata.

Each yoga has an id, a classical name, and a primary reference.
The detection logic lives in the individual rule modules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YogaDefinition:
    id: str
    name: str
    classical_basis: str
    category: str  # WEALTH / POWER / BENEFIC / CHALLENGING


YOGAS: dict[str, YogaDefinition] = {
    "GAJA_KESARI": YogaDefinition(
        id="GAJA_KESARI",
        name="Gaja Kesari Yoga",
        classical_basis="BPHS ch. 36",
        category="BENEFIC",
    ),
    "CHANDRA_MANGALA": YogaDefinition(
        id="CHANDRA_MANGALA",
        name="Chandra-Mangala Yoga",
        classical_basis="BPHS ch. 36",
        category="WEALTH",
    ),
    "DHANA_YOGA": YogaDefinition(
        id="DHANA_YOGA",
        name="Dhana Yoga",
        classical_basis="BPHS ch. 24",
        category="WEALTH",
    ),
    "RAJA_YOGA": YogaDefinition(
        id="RAJA_YOGA",
        name="Raja Yoga",
        classical_basis="BPHS ch. 39",
        category="POWER",
    ),
    "LAKSHMI_YOGA": YogaDefinition(
        id="LAKSHMI_YOGA",
        name="Lakshmi Yoga",
        classical_basis="Phaladeepika ch. 6",
        category="WEALTH",
    ),
    "PANCHA_MAHAPURUSHA": YogaDefinition(
        id="PANCHA_MAHAPURUSHA",
        name="Pancha Mahapurusha Yoga",
        classical_basis="BPHS ch. 75",
        category="BENEFIC",
    ),
    "NEECHA_BHANGA": YogaDefinition(
        id="NEECHA_BHANGA",
        name="Neecha Bhanga Raja Yoga",
        classical_basis="BPHS ch. 22",
        category="BENEFIC",
    ),
    "VIPARITA_RAJA": YogaDefinition(
        id="VIPARITA_RAJA",
        name="Viparita Raja Yoga",
        classical_basis="Phaladeepika ch. 6",
        category="CHALLENGING",
    ),
    "KEMADRUMA": YogaDefinition(
        id="KEMADRUMA",
        name="Kemadruma Yoga",
        classical_basis="BPHS ch. 36",
        category="CHALLENGING",
    ),
}
