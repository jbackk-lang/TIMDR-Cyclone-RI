"""Combines the four Alvey et al. (2026) alignment signals into one
verdict per snapshot, mirroring the shear+TDS -> verdict pattern used in
the sibling repo TIMDR-Tornado-NEXRAD (tornado_shear/api.py): a single,
explicit, three-way classification instead of a black-box score.
"""

from __future__ import annotations

from dataclasses import dataclass

from cyclone_ri.environment import EnvironmentSnapshot, favorable_environment
from cyclone_ri.tilt_alignment import Vector2D, favorable_tilt, low_level_compactness_score

COMPACTNESS_FAVORABLE_THRESHOLD = 0.5  # score >= this counts as "compact" -- see tilt_alignment.py docstring

VERDICT_LIKELY_ALIGN = "likely_to_align"
VERDICT_POSSIBLE_ALIGN = "possible_alignment"
VERDICT_UNFAVORABLE = "unfavorable_for_alignment"


@dataclass
class AlignmentAssessment:
    verdict: str
    n_favorable_signals: int
    compact_circulation: bool
    favorable_tilt_direction: bool
    favorable_environment: bool
    details: dict


def assess_alignment(
    radius_of_max_wind_km: float,
    tilt: Vector2D,
    shear: Vector2D,
    env: EnvironmentSnapshot,
) -> AlignmentAssessment:
    """Signal 1 (compactness) and signal 2 (tilt direction) come from
    tilt_alignment.py; signal 4 (environment) from environment.py.
    Signal 3 (precipitation/updraft) is intentionally NOT included here
    -- convective_favorability_score() needs a same-storm reference
    value that has no natural single-snapshot default, so folding it in
    would silently hide a required input. Call it separately and factor
    it in yourself if you have a reference value.

    Verdict rule (this repo's own aggregation, not from the paper,
    which reports each factor's statistical association separately
    rather than a combined single verdict):
      3 of 3 favorable  -> likely_to_align
      1-2 of 3 favorable -> possible_alignment
      0 of 3 favorable   -> unfavorable_for_alignment
    """
    compactness = low_level_compactness_score(radius_of_max_wind_km)
    compact = compactness >= COMPACTNESS_FAVORABLE_THRESHOLD
    tilt_ok = favorable_tilt(tilt, shear)
    env_ok = favorable_environment(env)

    n_favorable = sum([compact, tilt_ok, env_ok])
    if n_favorable == 3:
        verdict = VERDICT_LIKELY_ALIGN
    elif n_favorable == 0:
        verdict = VERDICT_UNFAVORABLE
    else:
        verdict = VERDICT_POSSIBLE_ALIGN

    return AlignmentAssessment(
        verdict=verdict,
        n_favorable_signals=n_favorable,
        compact_circulation=compact,
        favorable_tilt_direction=tilt_ok,
        favorable_environment=env_ok,
        details={
            "compactness_score": compactness,
            "tilt_magnitude_km": tilt.magnitude_km,
            "shear_magnitude_kt": shear.magnitude_km,
            "sst_c": env.sst_c,
            "mid_level_rh_pct": env.mid_level_rh_pct,
            "shear_kt": env.shear_kt,
        },
    )
