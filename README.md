# TIMDR-Cyclone-RI

Formalizes the four storm characteristics that precede tropical cyclone
vertical alignment and rapid intensification (RI), identified in a 2026
NOAA-led study of 27 years of Hurricane Hunter radar data. Built and
validated the same way as the rest of the TIMDR ecosystem
(pre-registration-style honesty about what's checked vs. not, positive/
negative controls, no post-hoc threshold tuning). Written in English --
like `TIMDR-Tornado-NEXRAD` -- because the source science and data
(NOAA/NHC) are English-language and US-centric.

## The science

Alvey et al. (2026, *JGR-Atmospheres*, DOI
[10.1029/2025JD045986](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JD045986))
compared 1997-2024 tropical cyclones that were initially tilted, split
into those that vertically aligned within 24h vs. those that stayed
persistently tilted, using TC-RADAR (27 years of NOAA Hurricane Hunter
airborne Doppler radar analyses). Four factors distinguished the two
groups:

1. **A strong, compact circulation near the ocean surface.**
2. **A favorable tilt direction** -- left-leaning of the environmental
   vertical wind shear vector, which makes the storm less susceptible
   to being torn apart by that shear.
3. **Stronger upward motion and heavier rainfall near the low-level
   center.**
4. **A favorable environment** -- warm ocean water, abundant mid-level
   moisture, relatively weak mid-level winds.

Full citations, including a companion 2023 GRL paper (Rogers et al.)
that supplies the one hard number used here (the 9-21 kt "moderate
shear" band), are in [`docs/SOURCES.md`](docs/SOURCES.md).

## What this operator is

- `cyclone_ri/tilt_alignment.py` -- signals 1 and 2: low-level
  circulation compactness (from radius of maximum wind), and whether
  the tilt vector (low-level center to mid-level center) sits in the
  "favorable", left-of-shear half-plane.
- `cyclone_ri/environment.py` -- signals 3 and 4: an environment
  favorability check (SST / mid-level RH / shear-magnitude thresholds,
  cited from the literature) and a convective-favorability score
  (rain rate + updraft strength relative to a reference/quiet value).
- `cyclone_ri/composite.py` -- combines compactness + tilt direction +
  environment into one verdict per snapshot: `likely_to_align`,
  `possible_alignment`, or `unfavorable_for_alignment` (mirrors the
  shear+TDS -> verdict pattern in the sibling repo
  `TIMDR-Tornado-NEXRAD`).
- `cyclone_ri/ri_outcome.py` -- a separate, independent piece: labels
  whether a storm's best-track wind series actually met NHC's official
  rapid-intensification definition (>=30 kt increase in 24h). This is
  the OUTCOME, not the precursor signals above.

**Every numeric threshold that isn't NHC's own official RI definition
is cited in `docs/SOURCES.md`, with an explicit note on which ones are
this repo's own operationalization of a qualitative finding** (the
source's plain-language summary describes several of the four signals
qualitatively, without a formula -- the full paper is paywalled).

## What has and hasn't been checked against real data

**Validated against real data**: `cyclone_ri/ri_outcome.py`, checked
against the real NHC HURDAT2 best-track record for the full 2019
Atlantic season (`data/hurdat2_2019_atlantic_ri_labels.json`,
computed directly from the raw 6-hourly wind speeds, not copied from a
secondary source). Hurricane Dorian's real 70-point wind series
(Category 1 to Category 5 in under 48h before hitting the Bahamas) is
stored in full and correctly classified as RI (35 kt/24h, exceeding the
30 kt/24h threshold) -- see `tests/test_ri_outcome_real_data.py`.
Humberto (2019) is a useful real negative case: it did become a major
hurricane, but its fastest 24h intensification (20 kt) falls short of
the RI threshold, so it's correctly labeled non-RI -- confirming the
classifier isn't just detecting "became a hurricane."

**NOT validated against real data**: `tilt_alignment.py` and
`environment.py` -- the actual precursor signals from Alvey et al.
(2026). These need TC-RADAR (radar-derived vortex centers and RMW) and
SHIPS developmental data (real per-storm environmental predictors);
neither was reachable from this sandbox's network (see
`docs/SOURCES.md`, "What this repo could NOT verify"). Only validated
here via synthetic self-tests (hand-constructed positive/negative
controls in `tests/test_tilt_alignment_synthetic.py` and
`tests/test_environment_synthetic.py`) -- the same honesty pattern used
throughout this ecosystem when a formal operator is implemented before
the specialist real-data source is available (see e.g.
`TIMDR-Geometry-Formalism`'s Weingarten operator history).

## Worked example: Hurricane Dorian (2019)

```python
from cyclone_ri.ri_outcome import is_rapid_intensification, max_24h_increase_kt

# Real HURDAT2 wind series, 2019-08-29 06Z to 2019-08-31 18Z (partial)
dorian_partial = [65, 70, 75, 75, 75, 75, 80, 90, 95, 100, 115]
print(max_24h_increase_kt(dorian_partial))   # 35.0 kt
print(is_rapid_intensification(dorian_partial))  # True -- meets NHC's official RI definition
```

## Install

```
pip install -r requirements.txt
python -m pytest tests/ -v
```

No hardware, no API keys, no downloads required -- the real 2019 season
data used for validation is bundled in `data/`.

## Repo layout

```
cyclone_ri/
  tilt_alignment.py   # signals 1, 2 (compactness, tilt-vs-shear direction)
  environment.py       # signals 3, 4 (environment favorability, convection)
  composite.py          # combines into one verdict
  ri_outcome.py          # real-data-validated RI outcome labeling
data/
  hurdat2_2019_atlantic_ri_labels.json   # real HURDAT2 2019 season data
docs/
  SOURCES.md    # full citations, honest data-access accounting
tests/
  test_tilt_alignment_synthetic.py
  test_environment_synthetic.py
  test_composite_synthetic.py
  test_ri_outcome_real_data.py   # the one real-data test file
```
