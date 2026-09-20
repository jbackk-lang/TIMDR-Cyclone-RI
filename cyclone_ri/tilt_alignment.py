"""Signals 1 and 2 from Alvey et al. (2026): low-level circulation
compactness, and tilt direction relative to environmental vertical wind
shear ("favorable tilt" = left-leaning of shear).

Geometry convention: all vectors are (east_km, north_km) in a local
tangent-plane approximation around the storm (fine for the ~100 km
scales involved; not valid for basin-scale distances). Angles are
standard math convention (counterclockwise from +x/east).

IMPORTANT: the source (NOAA AOML plain-language summary of Alvey et al.
2026) describes "tilt is often left-leaning of shear" qualitatively; it
does not give a numeric formula in the material available to this repo
(the full paper is paywalled). The `favorable_tilt` operationalization
below -- signed angle from shear vector to tilt vector, using the
left half-plane (0 to 180 degrees counterclockwise) as "favorable" -- is
this repo's own geometric reading of that qualitative description, not
a verbatim equation from the paper. See docs/SOURCES.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Vector2D:
    east_km: float
    north_km: float

    @property
    def magnitude_km(self) -> float:
        return math.hypot(self.east_km, self.north_km)

    @property
    def angle_deg(self) -> float:
        """Standard math convention: 0 = due east, 90 = due north,
        counterclockwise-positive."""
        return math.degrees(math.atan2(self.north_km, self.east_km))


def tilt_vector(low_level_center: tuple[float, float], mid_level_center: tuple[float, float]) -> Vector2D:
    """low_level_center / mid_level_center: (east_km, north_km) relative
    to any common local origin (e.g. the storm's initial fix). Returns
    the displacement from the low-level center to the mid-level center
    -- the standard tilt-vector convention in the TC literature (e.g.
    Reasor & Eastin 2012; Rogers et al. 2023)."""
    lo_e, lo_n = low_level_center
    mid_e, mid_n = mid_level_center
    return Vector2D(mid_e - lo_e, mid_n - lo_n)


def signed_angle_deg(from_vec: Vector2D, to_vec: Vector2D) -> float:
    """Signed angle (degrees, -180..180) to rotate from_vec onto
    to_vec, counterclockwise-positive. Uses atan2(cross, dot) so it is
    well-defined even when either vector has zero magnitude in one
    axis."""
    cross = from_vec.east_km * to_vec.north_km - from_vec.north_km * to_vec.east_km
    dot = from_vec.east_km * to_vec.east_km + from_vec.north_km * to_vec.north_km
    return math.degrees(math.atan2(cross, dot))


def favorable_tilt(tilt: Vector2D, shear: Vector2D) -> bool:
    """True if the tilt vector sits in the left half-plane relative to
    the shear vector's direction (0 to 180 degrees counterclockwise from
    shear) -- this repo's operationalization of "tilt is often
    left-leaning of shear" (Alvey et al. 2026). Returns False if either
    vector has ~zero magnitude (undefined direction)."""
    if tilt.magnitude_km < 1e-6 or shear.magnitude_km < 1e-6:
        return False
    angle = signed_angle_deg(shear, tilt)
    return 0.0 < angle < 180.0


def low_level_compactness_score(radius_of_max_wind_km: float, reference_radius_km: float = 60.0) -> float:
    """Signal 1: "a well-defined, tightly organized circulation near the
    sea surface" (quickly-aligning storms) vs. "a broader, weaker
    circulation" (persistently-tilted storms) -- Alvey et al. 2026,
    qualitative. Operationalized here as a simple ratio, clipped to
    [0, 1]: 1.0 = very compact (RMW << reference), 0.0 = RMW at or
    beyond the reference radius. `reference_radius_km=60` is an
    illustrative round number (typical broad/disorganized TC RMW is in
    the 60-100+ km range; compact, well-organized TCs are often
    20-40 km) -- NOT a threshold taken from the paper, which does not
    give one in the material available here. Treat this function as a
    reasonable synthetic-test scaffold, not a validated real-data
    classifier -- see README "What has and hasn't been checked".
    """
    if radius_of_max_wind_km <= 0:
        raise ValueError("radius_of_max_wind_km must be positive")
    score = 1.0 - (radius_of_max_wind_km / reference_radius_km)
    return max(0.0, min(1.0, score))
