"""Synthetic self-tests for tilt_alignment.py: hand-constructed positive
and negative controls, following the TIMDR ecosystem's anti-numerology
protocol (a geometric formula is only trustworthy if it passes obvious
hand-checkable cases before being trusted on ambiguous real data)."""

import math

import pytest

from cyclone_ri.tilt_alignment import (
    Vector2D,
    favorable_tilt,
    low_level_compactness_score,
    signed_angle_deg,
    tilt_vector,
)


def test_tilt_vector_is_displacement_from_low_to_mid_level():
    tv = tilt_vector(low_level_center=(0.0, 0.0), mid_level_center=(10.0, 0.0))
    assert tv.east_km == pytest.approx(10.0)
    assert tv.north_km == pytest.approx(0.0)
    assert tv.magnitude_km == pytest.approx(10.0)


def test_signed_angle_quarter_turns():
    east = Vector2D(1, 0)
    north = Vector2D(0, 1)
    west = Vector2D(-1, 0)
    south = Vector2D(0, -1)
    assert signed_angle_deg(east, north) == pytest.approx(90.0)
    assert signed_angle_deg(east, west) == pytest.approx(180.0) or signed_angle_deg(east, west) == pytest.approx(-180.0)
    assert signed_angle_deg(east, south) == pytest.approx(-90.0)
    assert signed_angle_deg(east, east) == pytest.approx(0.0)


def test_favorable_tilt_positive_control_left_of_shear():
    """Shear pointing due east; tilt pointing due north is 90 degrees
    counterclockwise (left) of shear -- must be favorable."""
    shear = Vector2D(10.0, 0.0)
    tilt = Vector2D(0.0, 5.0)
    assert favorable_tilt(tilt, shear) is True


def test_favorable_tilt_negative_control_right_of_shear():
    """Tilt pointing due south is to the right of eastward shear --
    must NOT be favorable."""
    shear = Vector2D(10.0, 0.0)
    tilt = Vector2D(0.0, -5.0)
    assert favorable_tilt(tilt, shear) is False


def test_favorable_tilt_negative_control_directly_downshear():
    """Tilt exactly aligned with shear direction (0 degrees) is the
    boundary case -- defined as NOT favorable (strictly left, not
    on-axis)."""
    shear = Vector2D(10.0, 0.0)
    tilt = Vector2D(5.0, 0.0)
    assert favorable_tilt(tilt, shear) is False


def test_favorable_tilt_undefined_for_zero_vectors():
    zero = Vector2D(0.0, 0.0)
    shear = Vector2D(10.0, 0.0)
    assert favorable_tilt(zero, shear) is False
    assert favorable_tilt(shear, zero) is False


def test_favorable_tilt_rotational_consistency():
    """Rotate a favorable configuration by an arbitrary angle -- must
    remain favorable, since favorability should depend only on the
    RELATIVE angle between tilt and shear, not on absolute compass
    direction."""
    for base_angle_deg in [0, 37, 90, 200, 350]:
        rad = math.radians(base_angle_deg)
        shear = Vector2D(10.0 * math.cos(rad), 10.0 * math.sin(rad))
        # tilt rotated 45 degrees counterclockwise from shear -> favorable
        tilt_rad = rad + math.radians(45)
        tilt = Vector2D(5.0 * math.cos(tilt_rad), 5.0 * math.sin(tilt_rad))
        assert favorable_tilt(tilt, shear) is True, f"failed at base_angle={base_angle_deg}"


def test_compactness_score_bounds():
    assert low_level_compactness_score(1.0, reference_radius_km=60.0) == pytest.approx(1.0, abs=0.02)
    assert low_level_compactness_score(60.0, reference_radius_km=60.0) == pytest.approx(0.0)
    assert low_level_compactness_score(120.0, reference_radius_km=60.0) == 0.0  # clipped, not negative


def test_compactness_score_positive_vs_negative_control():
    """Positive control: tight, well-organized RMW (25 km, typical of a
    compact/well-organized TC). Negative control: broad, disorganized
    RMW (90 km) -- must score meaningfully lower."""
    tight = low_level_compactness_score(25.0)
    broad = low_level_compactness_score(90.0)
    assert tight > broad
    assert tight > 0.5
    assert broad == 0.0


def test_compactness_score_rejects_nonpositive_radius():
    with pytest.raises(ValueError):
        low_level_compactness_score(0.0)
    with pytest.raises(ValueError):
        low_level_compactness_score(-5.0)
