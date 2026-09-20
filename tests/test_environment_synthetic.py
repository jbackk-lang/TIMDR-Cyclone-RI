"""Synthetic self-tests for environment.py: positive/negative controls
around each of the three literature-sourced thresholds (SST, mid-level
RH, moderate shear band). See module docstring in environment.py for
citations."""

import pytest

from cyclone_ri.environment import (
    MID_LEVEL_RH_THRESHOLD_PCT,
    SHEAR_MODERATE_BAND_KT,
    SST_THRESHOLD_C,
    EnvironmentSnapshot,
    convective_favorability_score,
    favorable_environment,
)


def test_favorable_environment_positive_control():
    """Classic RI-favorable environment: warm Gulf/Caribbean SST, moist
    mid-levels, shear squarely inside the moderate band."""
    env = EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=65.0, shear_kt=15.0)
    assert favorable_environment(env) is True


def test_favorable_environment_negative_control_cold_sst():
    env = EnvironmentSnapshot(sst_c=24.0, mid_level_rh_pct=65.0, shear_kt=15.0)
    assert favorable_environment(env) is False


def test_favorable_environment_negative_control_dry_midlevels():
    env = EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=20.0, shear_kt=15.0)
    assert favorable_environment(env) is False


def test_favorable_environment_negative_control_shear_too_strong():
    """Shear well above the moderate band (e.g. 35 kt) is a classic
    RI-inhibiting environment."""
    env = EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=65.0, shear_kt=35.0)
    assert favorable_environment(env) is False


def test_favorable_environment_boundary_shear_too_weak():
    """Shear below the moderate band (near-zero) is NOT flagged
    favorable by this operator, even though very weak shear is
    generally not harmful -- Rogers et al. (2023)'s finding was
    specifically that the tall-vortex RI advantage was most apparent in
    the MODERATE band, not that weak shear is bad. This test documents
    that distinction rather than asserting it's a flaw."""
    env = EnvironmentSnapshot(sst_c=29.0, mid_level_rh_pct=65.0, shear_kt=2.0)
    assert favorable_environment(env) is False


def test_threshold_constants_match_documented_sources():
    """Regression guard: if these constants ever get "tuned", the
    change should be a deliberate, documented edit to environment.py's
    docstring/docs/SOURCES.md -- not a silent drift. See docs/SOURCES.md
    for where each number comes from."""
    assert SST_THRESHOLD_C == 26.5
    assert MID_LEVEL_RH_THRESHOLD_PCT == 40.0
    assert SHEAR_MODERATE_BAND_KT == (9.0, 21.0)


def test_convective_favorability_positive_vs_negative_control():
    heavy_convection = convective_favorability_score(
        low_level_rain_rate_mm_hr=40.0,
        reference_quiet_rain_rate_mm_hr=5.0,
        updraft_ms=8.0,
        reference_quiet_updraft_ms=1.0,
    )
    quiet = convective_favorability_score(
        low_level_rain_rate_mm_hr=4.0,
        reference_quiet_rain_rate_mm_hr=5.0,
        updraft_ms=0.8,
        reference_quiet_updraft_ms=1.0,
    )
    assert heavy_convection > quiet
    assert heavy_convection > 10.0  # (40/5)*(8/1) = 64
    assert quiet < 1.0


def test_convective_favorability_rejects_nonpositive_reference():
    with pytest.raises(ValueError):
        convective_favorability_score(10.0, 0.0, 5.0, 1.0)
    with pytest.raises(ValueError):
        convective_favorability_score(10.0, 5.0, 5.0, 0.0)
