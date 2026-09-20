"""Synthetic self-tests for composite.py's three-way verdict, covering
all-favorable, all-unfavorable, and mixed cases."""

from cyclone_ri.composite import (
    VERDICT_LIKELY_ALIGN,
    VERDICT_POSSIBLE_ALIGN,
    VERDICT_UNFAVORABLE,
    assess_alignment,
)
from cyclone_ri.environment import EnvironmentSnapshot
from cyclone_ri.tilt_alignment import Vector2D


def test_all_three_favorable_gives_likely_align():
    result = assess_alignment(
        radius_of_max_wind_km=25.0,
        tilt=Vector2D(0.0, 5.0),
        shear=Vector2D(10.0, 0.0),
        env=EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=65.0, shear_kt=15.0),
    )
    assert result.verdict == VERDICT_LIKELY_ALIGN
    assert result.n_favorable_signals == 3
    assert result.compact_circulation is True
    assert result.favorable_tilt_direction is True
    assert result.favorable_environment is True


def test_all_three_unfavorable_gives_unfavorable():
    result = assess_alignment(
        radius_of_max_wind_km=100.0,  # broad, disorganized
        tilt=Vector2D(0.0, -5.0),  # right of shear
        shear=Vector2D(10.0, 0.0),
        env=EnvironmentSnapshot(sst_c=22.0, mid_level_rh_pct=15.0, shear_kt=40.0),
    )
    assert result.verdict == VERDICT_UNFAVORABLE
    assert result.n_favorable_signals == 0


def test_mixed_signals_give_possible_alignment():
    """Compact circulation and favorable tilt, but an unfavorable
    (too-cold) environment -- a real "leaning towards intensification
    structurally, but the ocean/atmosphere isn't cooperating" case."""
    result = assess_alignment(
        radius_of_max_wind_km=25.0,
        tilt=Vector2D(0.0, 5.0),
        shear=Vector2D(10.0, 0.0),
        env=EnvironmentSnapshot(sst_c=22.0, mid_level_rh_pct=65.0, shear_kt=15.0),
    )
    assert result.verdict == VERDICT_POSSIBLE_ALIGN
    assert result.n_favorable_signals == 2
    assert result.compact_circulation is True
    assert result.favorable_tilt_direction is True
    assert result.favorable_environment is False


def test_details_dict_carries_raw_inputs_for_audit():
    result = assess_alignment(
        radius_of_max_wind_km=25.0,
        tilt=Vector2D(0.0, 5.0),
        shear=Vector2D(10.0, 0.0),
        env=EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=65.0, shear_kt=15.0),
    )
    assert result.details["sst_c"] == 29.0
    assert result.details["shear_kt"] == 15.0
    assert result.details["tilt_magnitude_km"] == 5.0
