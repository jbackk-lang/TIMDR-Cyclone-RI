# Sources

## Primary science (the "four signs" this repo formalizes)

Alvey, G.R. III, et al. (2026). *Characteristics distinguishing tropical
cyclones that vertically align from those that remain persistently
tilted.* Journal of Geophysical Research: Atmospheres.
DOI: [10.1029/2025JD045986](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JD045986)

Plain-language summary (NOAA AOML, published 2026-07-22):
["To align or not align: decades of Hurricane Hunter radar data yield insights on rapid intensification"](https://www.aoml.noaa.gov/decades-of-hurricane-hunter-radar-data-yield-insights-on-rapid-intensification/)

Authors: University of Miami Rosenstiel School, University of Miami
Frost Institute for Data Science and Computing, NOAA AOML Hurricane
Research Division, CIMAS. Lead: George "Trey" Alvey, Ph.D.

Method: compared 1997-2024 tropical cyclones that were initially tilted,
split into those that became vertically aligned within 24h vs. those
that remained persistently tilted, using 27 years / 1,510 radar analyses
from TC-RADAR (see below).

**The four factors** (paraphrased from the plain-language summary, since
the exact statistical thresholds are in the paywalled paper, not the
blog post -- this repo's numeric thresholds are documented as *this
repo's own operationalization*, not verbatim equations from Alvey et
al., wherever the source is qualitative rather than an equation):

1. A strong, compact circulation near the ocean surface (quickly-aligning
   storms) vs. broader/weaker (persistently-tilted storms).
2. Favorable tilt direction: in storms that align, the tilt is often
   *left-leaning* relative to the environmental vertical wind shear
   vector, making the storm less susceptible to the shear.
3. Stronger upward motion and heavier rainfall near the low-level center.
4. Warm ocean water, abundant mid-level moisture, and relatively weak
   mid-level winds (a i.e. weak-to-moderate environmental shear).

## Supporting/related science

Rogers, R., Reasor, P., Zhang, J.A., et al. (2023). *Relating a Simple
Vortex Tilt Metric to Tropical Cyclone Intensity and Intensity Change.*
Geophysical Research Letters. DOI:
[10.1029/2022GL101877](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2022GL101877)

Plain-language summary (NOAA AOML, 2023-04-24):
["Study showing the relationship between how tilted a tropical cyclone vortex is and how fast it may intensify"](https://www.aoml.noaa.gov/hurricane_blog/study-showing-the-relationship-between-how-tilted-a-tropical-cyclone-vortex-is-and-how-fast-it-may-intensify-published-in-geophysical-research-letters/)

Introduces *Dynamic Height of Vortex (Dynamic HOV)*: the height at which
tangential wind speed decays to 40% of its value at 2 km. All TCs that
intensified most rapidly (largest 24h Pmin decrease) had Dynamic HOV
> 10 km. The favorability of a tall vortex for rapid strengthening was
most apparent when environmental vertical wind shear (VWS) was
*moderate* (roughly 9-21 kt) -- not weak enough to be irrelevant, not
strong enough to halt intensification outright. This repo's
`environment.py` moderate-shear band is taken directly from this number.

## Data

**TC-RADAR** (Tropical Cyclone Radar Archive of Doppler Analyses with
Re-centering) -- 27 years (1997-2024) of NOAA Hurricane Hunter airborne
Doppler radar analyses, the dataset both studies above are built on.
Listing: https://www.aoml.noaa.gov/ftp/pub/hrd/data/radar/level3/
**Not used directly in this repo** -- level-3 gridded radar analyses
require domain-specific tooling (map projections, recentering, vertical
interpolation) beyond what was practical to stand up in this session.
This is the single biggest gap between what this repo validates and
what the source papers actually measured -- see README "What has and
hasn't been checked against real data".

**HURDAT2** (NHC Atlantic hurricane database best track) -- used in this
repo for real (not synthetic) intensity-change outcome labels.
Fetched: https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2024-040425.txt
(2026-09-20). Format documented at
https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atlantic.pdf
Official RI definition used throughout (NHC): an increase of at least
30 kt in the maximum sustained surface wind speed in a 24-hour period.
The extracted 2019 Atlantic season labels are in
`data/hurdat2_2019_atlantic_ri_labels.json`, computed directly from the
raw best-track 6-hourly wind speeds -- not copied from any secondary
source.

## What this repo could NOT verify from this environment

SHIPS (Statistical Hurricane Intensity Prediction Scheme) developmental
data, which carries the real per-storm, per-6h environmental predictors
(shear magnitude/direction, SST, mid-level RH) used operationally --
`nhc.noaa.gov`/`rammb2.cira.colostate.edu` FTP/data endpoints were not
reachable from this sandbox's network allowlist. `environment.py`'s
thresholds are therefore taken from the published literature (Rogers et
al. 2023's VWS band; standard RI-index SST/RH thresholds cited widely in
the RI literature, e.g. Kaplan & DeMaria-style work) rather than from a
real per-storm predictor file this repo pulled itself. Flagged
explicitly in README rather than presented as directly data-validated.
