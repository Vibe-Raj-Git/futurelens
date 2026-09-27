"""
Yoga detector.

Runs every yoga rule against a chart and returns the list of
YogaResults.
"""

from __future__ import annotations

from dataclasses import dataclass

from futurelens.models.yoga import YogaResult
from futurelens.yogas.rules import (
    chandra_mangala,
    kemadruma,
    dhana_yoga,
    gaja_kesari,
    lakshmi_yoga,
    neecha_bhanga,
    pancha_mahapurusha,
    raja_yoga,
    viparita_raja,
)


ALL_DETECTORS = (
    gaja_kesari.detect,
    chandra_mangala.detect,
    kemadruma.detect,
    dhana_yoga.detect,
    raja_yoga.detect,
    lakshmi_yoga.detect,
    pancha_mahapurusha.detect,
    neecha_bhanga.detect,
    viparita_raja.detect,
)


@dataclass
class YogaReport:
    """The result of running all yoga detectors against a chart."""

    results: list[YogaResult]

    @property
    def present(self) -> list[YogaResult]:
        return [r for r in self.results if r.present]

    @property
    def absent(self) -> list[YogaResult]:
        return [r for r in self.results if not r.present]

    def by_id(self, yoga_id: str) -> YogaResult | None:
        for r in self.results:
            if r.yoga_id == yoga_id:
                return r
        return None

    def summary(self) -> dict:
        return {
            "total": len(self.results),
            "present": len(self.present),
            "absent": len(self.absent),
            "present_ids": [r.yoga_id for r in self.present],
        }


def detect_yogas(chart) -> YogaReport:
    """Run every yoga detector against a chart."""
    results: list[YogaResult] = []
    for detector in ALL_DETECTORS:
        try:
            results.append(detector(chart))
        except Exception:
            # A single detector failure should not kill the report.
            continue
    return YogaReport(results=results)
