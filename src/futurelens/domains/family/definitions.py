"""
Classical FAMILY domain definitions.

Family analysis in Jyotish is distributed across six bhavas and
seven significators. There is no single "family house" — different
houses govern different relationships.

References:
  BPHS ch. 24 (Bhava phala)
  Phaladeepika ch. 6 (Bhava phala)
  Saravali ch. 30-34 (Karakas)
"""

from __future__ import annotations


# The six bhavas that carry family significations.
FAMILY_HOUSES: tuple[int, ...] = (2, 4, 5, 7, 9, 12)

# Reason for each family house's relevance.
FAMILY_HOUSE_REASONS: dict[int, str] = {
    2: "family, lineage, close relatives",
    4: "mother, home, domestic happiness",
    5: "children, progeny",
    7: "spouse, marriage, partnership",
    9: "father, guru, ancestral merit",
    12: "ancestral karma, distant relatives",
}

# Natural family significators (karakas).
# Each graha carries a specific family relationship.
FAMILY_SIGNIFICATORS: tuple[str, ...] = (
    "MOON",      # mother
    "SUN",       # father
    "MARS",      # brothers (especially younger)
    "JUPITER",   # husband (for female native), children
    "VENUS",     # wife (for male native), marriage
    "MERCURY",   # paternal uncle, family commerce
    "SATURN",    # paternal grandfather, longevity
)

# Specific relationship signification of each graha.
SIGNIFICATOR_REASONS: dict[str, str] = {
    "MOON": "mother, emotional bond of the family",
    "SUN": "father, paternal authority",
    "MARS": "brothers, siblings, courage in family",
    "JUPITER": "husband (for female native), children, family guru",
    "VENUS": "wife (for male native), marriage, family harmony",
    "MERCURY": "paternal uncle, family commerce and communication",
    "SATURN": "paternal grandfather, longevity, family endurance",
}

# Specific relationship configurations the engine evaluates.
# Each entry is (relationship_name, primary_house, primary_lord_role,
#                primary_significator)
FAMILY_RELATIONSHIPS: tuple[dict, ...] = (
    {
        "name": "mother",
        "house": 4,
        "significator": "MOON",
        "rule_id": "FAMILY-RELATIONSHIP-001",
    },
    {
        "name": "father",
        "house": 9,
        "significator": "SUN",
        "rule_id": "FAMILY-RELATIONSHIP-001",
    },
    {
        "name": "spouse",
        "house": 7,
        "significator": "VENUS",
        "rule_id": "FAMILY-RELATIONSHIP-001",
    },
    {
        "name": "children",
        "house": 5,
        "significator": "JUPITER",
        "rule_id": "FAMILY-RELATIONSHIP-001",
    },
    {
        "name": "siblings",
        "house": 3,
        "significator": "MARS",
        "rule_id": "FAMILY-RELATIONSHIP-001",
    },
)

# Yogas that promote into family evidence.
FAMILY_RELEVANT_YOGAS: tuple[str, ...] = (
    "CHANDRA_MANGALA",       # domestic harmony, family prosperity
    "GAJA_KESARI",           # family support, respected lineage
    "KEMADRUMA",             # family isolation, loneliness of mother
)

DUSTHANAS: tuple[int, ...] = (6, 8, 12)
KENDRAS: tuple[int, ...] = (1, 4, 7, 10)
TRIKONAS: tuple[int, ...] = (1, 5, 9)
FAVOURABLE_HOUSES: tuple[int, ...] = (1, 2, 4, 5, 7, 9, 10, 11)

BENEFICS: tuple[str, ...] = ("JUPITER", "VENUS", "MERCURY", "MOON")
MALEFICS: tuple[str, ...] = ("SUN", "MARS", "SATURN", "RAHU", "KETU")


def is_family_house(house: int) -> bool:
    return house in FAMILY_HOUSES


def is_dusthana(house: int) -> bool:
    return house in DUSTHANAS


def is_kendra(house: int) -> bool:
    return house in KENDRAS


def is_trikona(house: int) -> bool:
    return house in TRIKONAS
