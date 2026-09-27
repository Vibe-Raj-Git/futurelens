from __future__ import annotations

from futurelens.models.upagraha import UpagrahaName, UpagrahaPosition
from futurelens.upagraha.sun_chain import validate_sun_chain


def check_sun_chain_invariants(
    chain: dict[UpagrahaName, UpagrahaPosition],
) -> None:
    """Raises InvariantViolation on failure."""
    validate_sun_chain(chain)
