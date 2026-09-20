"""Rapid intensification OUTCOME labeling -- i.e. did the storm actually
rapidly intensify -- as distinct from the PRECURSOR signals in
tilt_alignment.py / environment.py. This module is the one piece of
this repo directly validated against real best-track data (NHC HURDAT2,
see docs/SOURCES.md and data/hurdat2_2019_atlantic_ri_labels.json).

NHC's official definition (used unchanged here): rapid intensification
is an increase of at least 30 kt in the maximum sustained surface wind
speed within any 24-hour period.
"""

from __future__ import annotations

from dataclasses import dataclass

RI_THRESHOLD_KT_PER_24H = 30.0
SYNOPTIC_STEPS_PER_24H = 4  # HURDAT2 best track is 6-hourly


@dataclass
class WindObservation:
    wind_kt: float


def max_24h_increase_kt(wind_series_kt: list[float]) -> float:
    """wind_series_kt: 6-hourly max sustained wind speeds (kt), in
    chronological order (matching HURDAT2 best-track spacing). Returns
    the largest increase over any 24h (4-step) window; negative if the
    storm only ever weakened. Raises if fewer than 5 points (need at
    least one full 24h window)."""
    n = len(wind_series_kt)
    if n <= SYNOPTIC_STEPS_PER_24H:
        raise ValueError(
            f"need at least {SYNOPTIC_STEPS_PER_24H + 1} 6-hourly observations "
            f"for a 24h window, got {n}"
        )
    return max(
        wind_series_kt[i + SYNOPTIC_STEPS_PER_24H] - wind_series_kt[i]
        for i in range(n - SYNOPTIC_STEPS_PER_24H)
    )


def is_rapid_intensification(wind_series_kt: list[float]) -> bool:
    """True iff the storm's best-track wind series contains a 24h
    increase meeting NHC's official >=30kt RI threshold."""
    return max_24h_increase_kt(wind_series_kt) >= RI_THRESHOLD_KT_PER_24H
