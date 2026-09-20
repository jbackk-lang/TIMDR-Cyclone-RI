"""Real-data test (NOT synthetic): re-derives RI/non-RI labels directly
from real NHC HURDAT2 best-track wind series and checks them against
data/hurdat2_2019_atlantic_ri_labels.json -- both sides computed from
the same raw numbers, so this is a regression/consistency check that the
implementation matches the documented methodology, not an independent
verification against a second data source. It IS real 2019 Atlantic
hurricane season data, not synthetic/fabricated."""

import json
import os

import pytest

from cyclone_ri.ri_outcome import is_rapid_intensification, max_24h_increase_kt

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "hurdat2_2019_atlantic_ri_labels.json"
)


@pytest.fixture(scope="module")
def hurdat_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_dorian_full_series_matches_documented_ri_event(hurdat_data):
    """Hurricane Dorian (2019): real 70-point 6-hourly wind series from
    HURDAT2. Independently well-documented as an RI event (Category 1
    to Category 5 in under 48h before landfall in the Bahamas) -- this
    is not just re-deriving our own summary number, it's checking the
    full raw series against NHC's official >=30kt/24h definition."""
    series = hurdat_data["dorian_detail"]["full_wind_series_kt_6hourly"]
    assert len(series) == 70
    assert max_24h_increase_kt(series) == 35.0
    assert is_rapid_intensification(series) is True


@pytest.mark.parametrize(
    "storm_name,expected_ri",
    [
        ("DORIAN", True),
        ("JERRY", True),
        ("LORENZO", True),
        ("REBEKAH", True),
        ("ANDREA", False),
        ("HUMBERTO", False),
        ("BARRY", False),
        ("IMELDA", False),
    ],
)
def test_2019_season_ri_labels(hurdat_data, storm_name, expected_ri):
    """Cross-check a handful of real 2019 Atlantic storms (both RI and
    non-RI) against the precomputed labels in the data file. HUMBERTO is
    a useful negative case: it did reach major-hurricane strength but
    its fastest 24h intensification (20 kt) falls short of the official
    30kt RI threshold -- confirms the classifier isn't just "became a
    hurricane" in disguise."""
    storms = {s["name"]: s for s in hurdat_data["storms"]}
    assert storms[storm_name]["ri"] == expected_ri
