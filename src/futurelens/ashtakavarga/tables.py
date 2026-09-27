"""
Ashtakavarga tables loader.

Reads rulebook/ashtakavarga_tables.yaml and exposes it as a Python
dict. The YAML is the canonical source; this module is a thin
loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


SUBJECTS: tuple[str, ...] = (
    "SUN", "MOON", "MARS", "MERCURY",
    "JUPITER", "VENUS", "SATURN",
)

CONTRIBUTORS: tuple[str, ...] = (
    "SUN", "MOON", "MARS", "MERCURY",
    "JUPITER", "VENUS", "SATURN", "LAGNA",
)

# BAV total per subject (classical constants).
BAV_TOTALS: dict[str, int] = {
    "SUN": 48,
    "MOON": 49,
    "MARS": 39,
    "MERCURY": 54,
    "JUPITER": 56,
    "VENUS": 52,
    "SATURN": 39,
}

# Sarvastakavarga total (sum of BAV totals).
SAV_TOTAL: int = 337


def _find_tables_file() -> Path:
    """Walk up from this file to find the project root."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "rulebook" / "ashtakavarga_tables.yaml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not find rulebook/ashtakavarga_tables.yaml in any "
        "parent directory."
    )


def load_tables() -> dict[str, dict[str, list[int]]]:
    """Load the Ashtakavarga bindu contribution tables."""
    path = _find_tables_file()
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    tables: dict[str, dict[str, list[int]]] = {}
    for subject in SUBJECTS:
        if subject not in raw:
            raise ValueError(f"Missing subject in tables: {subject}")
        tables[subject] = {}
        for contributor in CONTRIBUTORS:
            if contributor not in raw[subject]:
                raise ValueError(
                    f"Missing contributor {contributor} "
                    f"for subject {subject}"
                )
            tables[subject][contributor] = list(raw[subject][contributor])
    return tables
