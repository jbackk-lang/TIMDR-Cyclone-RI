"""Signals 3 and 4 from Alvey et al. (2026): precipitation/updraft
structure near the low-level center, and environmental favorability
(warm SST, abundant mid-level moisture, weak-to-moderate mid-level
winds).

Numeric thresholds and their sources (see docs/SOURCES.md for full
citations):

- SST >= 26.5 C: the long-established minimum sea-surface temperature
  for tropical cyclone maintenance/intensification (Palmer 1948 and
  decades of subsequent TC literature; used essentially unchanged in
  operational genesis/intensity guidance today).
- Mid-level (700-500 hPa) relative humidity >= 40%: a standard
  moisture-favorability cutoff used in RI-index-style statistical
  predictors (e.g. SHIPS RI index moisture terms).
- Vertical wind shear in the 9-21 kt "moderate" band: taken directly
  from Rogers et al. (2023, GRL) -- the specific numeric range in which
  a tall vortex (large Dynamic HOV) was most clearly favored to
  intensify faster than a shallow one. Alvey et al. (2026)'s own
  language ("relatively weak winds in the middle levels") is
  qualitative and consistent with the lower half of this band, but
  supplies no number of its own in the material available to this repo.

These are real, cited thresholds from the literature -- but they have
NOT been re-derived or re-validated against a real per-storm
environmental dataset from within this repo (SHIPS developmental data
was not reachable from this sandbox -- see docs/SOURCES.md). Treat
`favorable_environment` as literature-grounded, not independently
data-validated here.
"""

from __future__ import annotations

from dataclasses import dataclass

SST_THRESHOLD_C = 26.5
MID_LEVEL_RH_THRESHOLD_PCT = 40.0
SHEAR_MODERATE_BAND_KT = (9.0, 21.0)


@dataclass
class EnvironmentSnapshot:
    sst_c: float
    mid_level_rh_pct: float
    shear_kt: float


def favorable_environment(env: EnvironmentSnapshot) -> bool:
    """All three conditions must hold: warm-enough SST, moist-enough
    mid-levels, and shear within the moderate band associated with
    alignment/RI favorability (see module docstring for sources)."""
    lo, hi = SHEAR_MODERATE_BAND_KT
    return (
        env.sst_c >= SST_THRESHOLD_C
        and env.mid_level_rh_pct >= MID_LEVEL_RH_THRESHOLD_PCT
        and lo <= env.shear_kt <= hi
    )


def convective_favorability_score(
    low_level_rain_rate_mm_hr: float,
    reference_quiet_rain_rate_mm_hr: float,
    updraft_ms: float,
    reference_quiet_updraft_ms: float = 1.0,
) -> float:
    """Signal 3: "stronger upward motion and heavier rainfall near the
    low-level center favor alignment" (Alvey et al. 2026, qualitative --
    no numeric formula given in the material available here). Returns a
    simple, illustrative combined ratio (rain-rate ratio times
    updraft ratio, each floored at 0) rather than a validated index --
    this is a scaffold for the synthetic self-tests, not a real-data
    classifier. `reference_quiet_*` should be a comparison value from a
    quiet/undisturbed period or location, mirroring the "compare against
    a real background, not a fixed constant" discipline used elsewhere
    in the TIMDR ecosystem's anti-numerology protocol.
    """
    if reference_quiet_rain_rate_mm_hr <= 0 or reference_quiet_updraft_ms <= 0:
        raise ValueError("reference values must be positive")
    rain_ratio = max(0.0, low_level_rain_rate_mm_hr / reference_quiet_rain_rate_mm_hr)
    updraft_ratio = max(0.0, updraft_ms / reference_quiet_updraft_ms)
    return rain_ratio * updraft_ratio
