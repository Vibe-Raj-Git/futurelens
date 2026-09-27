"""
Planetary and house relations.

Conjunction, aspect, exchange, and house-from-house relations used
by the yoga engine.

Aspects here are WHOLE-SIGN aspects, per Parashara. Not degree-based
Western aspects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# --- House groups ---------------------------------------------------------

KENDRAS: tuple[int, ...] = (1, 4, 7, 10)
TRIKONAS: tuple[int, ...] = (1, 5, 9)
DUSTHANAS: tuple[int, ...] = (6, 8, 12)
UPACHAYAS: tuple[int, ...] = (3, 6, 10, 11)


def is_kendra(house: int) -> bool:
    return house in KENDRAS


def is_trikona(house: int) -> bool:
    return house in TRIKONAS


def is_dusthana(house: int) -> bool:
    return house in DUSTHANAS


# --- Whole-sign aspects ---------------------------------------------------
#
# Parashara's aspect rules:
#   - All grahas aspect the 7th house/sign from themselves.
#   - Mars additionally aspects the 4th and 8th.
#   - Jupiter additionally aspects the 5th and 9th.
#   - Saturn additionally aspects the 3rd and 10th.
#   - Rahu aspects the 5th, 7th, and 9th (in some traditions).

ASPECT_OFFSETS: dict[str, tuple[int, ...]] = {
    "SUN":     (7,),
    "MOON":    (7,),
    "MARS":    (4, 7, 8),
    "MERCURY": (7,),
    "JUPITER": (5, 7, 9),
    "VENUS":   (7,),
    "SATURN":  (3, 7, 10),
    "RAHU":    (5, 7, 9),
    "KETU":    (5, 7, 9),
}


# --- Basic relations ------------------------------------------------------

def same_sign(a: Any, b: Any) -> bool:
    """True if two objects with .sign_index are in the same sign."""
    return a.sign_index == b.sign_index


def conjunct(chart, graha_a: str, graha_b: str) -> bool:
    """True if two grahas occupy the same sign."""
    a = chart.grahas[graha_a]
    b = chart.grahas[graha_b]
    return a.sign_index == b.sign_index


def grahas_conjunct(chart, names: list[str]) -> bool:
    """True if all named grahas occupy the same sign."""
    if len(names) < 2:
        return False
    sign = chart.grahas[names[0]].sign_index
    return all(chart.grahas[n].sign_index == sign for n in names)


def aspects(chart, graha_from: str, graha_to: str) -> bool:
    """True if graha_from aspects graha_to by whole-sign aspect."""
    src = chart.grahas[graha_from]
    dst = chart.grahas[graha_to]
    offsets = ASPECT_OFFSETS.get(graha_from, (7,))
    for offset in offsets:
        if (src.sign_index + offset - 1) % 12 == dst.sign_index:
            return True
    return False


def mutual_aspect(chart, graha_a: str, graha_b: str) -> bool:
    """True if two grahas aspect each other."""
    return aspects(chart, graha_a, graha_b) and aspects(chart, graha_b, graha_a)


def exchange(chart, graha_a: str, graha_b: str) -> bool:
    """True if grahas A and B are in each other's signs (parivartana)."""
    a = chart.grahas[graha_a]
    b = chart.grahas[graha_b]
    a_sign = a.sign_index
    b_sign = b.sign_index

    from futurelens.grahas.definitions import GRAHA_BY_NAME

    a_owns = GRAHA_BY_NAME[graha_a].own_signs
    b_owns = GRAHA_BY_NAME[graha_b].own_signs

    return b_sign in a_owns and a_sign in b_owns


def house_from_house(house_a: int, house_b: int) -> int:
    """House number of B counted from A."""
    return ((house_b - house_a) % 12) + 1


def graha_in_kendra_from_graha(chart, graha_a: str, graha_b: str) -> bool:
    """True if graha_a is in a kendra from graha_b."""
    a_sign = chart.grahas[graha_a].sign_index
    b_sign = chart.grahas[graha_b].sign_index
    distance = ((a_sign - b_sign) % 12) + 1
    return distance in (1, 4, 7, 10)
