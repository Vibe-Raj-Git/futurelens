"""
Classical career domain definitions.

Career-relevant houses, significators, and reasons.

References:
  BPHS ch. 24 (Bhava phala)
  Phaladeepika ch. 6 (Bhava phala)
  Standard 10/6/2/11 career framework
"""

from __future__ import annotations


CAREER_HOUSES: tuple[int, ...] = (10, 6, 2, 11)

CAREER_HOUSE_REASONS: dict[int, str] = {
    10: "profession, career, status, public role",
    6: "service, competition, daily work, subordinates",
    2: "income from work, earned resources",
    11: "gains from profession, recognition, network",
}

CAREER_SIGNIFICATORS: tuple[str, ...] = (
    "SUN",      # authority, government, leadership
    "SATURN",   # discipline, service, long-term work
    "MERCURY",  # commerce, communication, analysis
    "JUPITER",  # teaching, advisory, wisdom-based work
    "MARS",     # execution, engineering, technical work
)

SIGNIFICATOR_REASONS: dict[str, str] = {
    "SUN": "authority, government, leadership, status",
    "SATURN": "discipline, service, long-term labour",
    "MERCURY": "commerce, communication, analysis, trade",
    "JUPITER": "teaching, advisory, law, wisdom-based work",
    "MARS": "execution, engineering, technical work, courage",
}

DUSTHANAS: tuple[int, ...] = (6, 8, 12)
KENDRAS: tuple[int, ...] = (1, 4, 7, 10)
TRIKONAS: tuple[int, ...] = (1, 5, 9)

# For career, benefics in the 10th from Moon or Lagna = Amala Yoga.
BENEFICS: tuple[str, ...] = ("JUPITER", "VENUS", "MERCURY")

# Yogas that, when present, promote into career evidence.
CAREER_RELEVANT_YOGAS: tuple[str, ...] = (
    "RAJA_YOGA",
    "PANCHA_MAHAPURUSHA",
    "DHANA_YOGA",
)


def is_career_house(house: int) -> bool:
    return house in CAREER_HOUSES


def is_dusthana(house: int) -> bool:
    return house in DUSTHANAS


def is_kendra(house: int) -> bool:
    return house in KENDRAS


def is_trikona(house: int) -> bool:
    return house in TRIKONAS
