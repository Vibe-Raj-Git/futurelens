"""
Classical wealth domain definitions.

Wealth-relevant houses, lords, significators, and their reasons.

References:
  BPHS ch. 24 (Dhana yogas)
  Phaladeepika ch. 6 (Bhava phala)
  Widely used 2/5/9/11 wealth framework
"""

from __future__ import annotations


# Houses that the classical texts associate with wealth.
WEALTH_HOUSES: tuple[int, ...] = (2, 5, 9, 11)

# Reason for each house's wealth relevance. Used in evidence notes.
WEALTH_HOUSE_REASONS: dict[int, str] = {
    2: "accumulated wealth, family resources",
    5: "speculation, investments, inheritance",
    9: "fortune, dharma, guru's grace",
    11: "gains, income, fulfillment of desires",
}

# Natural wealth significators (karakas).
WEALTH_SIGNIFICATORS: tuple[str, ...] = (
    "JUPITER",   # primary dhana karaka
    "VENUS",     # luxury, value, resources
    "MERCURY",   # commerce, trade, calculation
    "MOON",      # liquidity, public, fluctuations
    "SATURN",    # long-term accumulation, discipline
)

# For each significator, a classical reason.
SIGNIFICATOR_REASONS: dict[str, str] = {
    "JUPITER": "primary dhana karaka; natural giver of abundance",
    "VENUS": "value, luxury, and resources; lakshmi karaka",
    "MERCURY": "commerce, trade, calculation; business karaka",
    "MOON": "liquidity, public wealth, cash flow",
    "SATURN": "long-term accumulation, discipline, delayed wealth",
}

# Houses counted as dusthanas. Being in one weakens a wealth lord.
DUSTHANAS: tuple[int, ...] = (6, 8, 12)

# Kendra houses. Strong kendra placement of a wealth lord is favorable.
KENDRAS: tuple[int, ...] = (1, 4, 7, 10)

# Trikona houses. Strong trikona placement of a wealth lord is favorable.
TRIKONAS: tuple[int, ...] = (1, 5, 9)

# Benefic grahas. Benefic association with a wealth lord is favorable.
BENEFICS: tuple[str, ...] = ("JUPITER", "VENUS", "MERCURY", "MOON")

# Malefic grahas. Malefic association with a wealth lord is adverse.
MALEFICS: tuple[str, ...] = ("SUN", "MARS", "SATURN", "RAHU", "KETU")


def is_wealth_house(house: int) -> bool:
    return house in WEALTH_HOUSES


def is_dusthana(house: int) -> bool:
    return house in DUSTHANAS


def is_kendra(house: int) -> bool:
    return house in KENDRAS


def is_trikona(house: int) -> bool:
    return house in TRIKONAS


# Yogas that, when present, promote into wealth evidence.
WEALTH_RELEVANT_YOGAS: tuple[str, ...] = (
    "DHANA_YOGA",
    "RAJA_YOGA",
    "LAKSHMI_YOGA",
    "GAJA_KESARI",
    "CHANDRA_MANGALA",
)
