# Portfolio summary

## Project

**Tidal Blade Test Analysis** is a Python research-software repository for processing and validating TDMS data from full-scale composite tidal blade structural testing. It is based on legacy FastBlade / LoadTide analysis scripts and reorganises them into a public, reusable repository structure.

## Technical contribution

The repository demonstrates how exploratory laboratory data-processing scripts can be converted into maintainable research software:

- original TDMS workflows are preserved under `legacy/` for provenance;
- reusable calculations are moved into a Python package under `src/`;
- public synthetic tests verify FFT, damping, static calibration, fatigue-cycle, and actuator/root-bending-moment helper logic;
- raw TDMS data and Excel logs are excluded from version control;
- GitHub Actions, `pyproject.toml`, citation metadata, and documentation make the project suitable for portfolio review.

## Engineering context

The main public scope is the first FastBlade full-scale tidal blade fatigue test and the single-vs-multi-actuator comparison. The original scripts cover common structural-test workflows:

- TDMS file joining and post-processing;
- channel inventory and resampling;
- natural-frequency and damping analysis;
- static load-displacement checks;
- fatigue load-history processing;
- root-bending-moment checks for point-load actuator setups;
- RIO/STC signal comparison.

## Related research context

Later FastBlade work on clamping/load-introduction and destructive/failure testing is documented as related experimental context. The current repository does not claim to reproduce DIC, clamping preload, acoustic-emission, or failure-analysis workflows unless those data and scripts are added later.

## Why this matters

Laboratory test data often starts as one-off scripts tied to local paths and private data. This repository shows how to convert that into a maintainable software asset without losing the original provenance or over-claiming reproducibility.

## Current limitations

- The public repository does not include raw TDMS data.
- The full legacy pipeline is not yet fully refactored into callable functions.
- Some original scripts still need manual validation against the private experiment archive before being replaced.
- DIC/clamping and destructive-test/failure-analysis workflows are documented as related context only.

## Next development steps

1. Add a small anonymised TDMS fixture or generated TDMS example.
2. Refactor the join/resample workflow into tested functions.
3. Add a validation report that checks sample counts, time increments, channel availability, and drift.
4. Replace duplicated `Main_Analysis*` scripts with a single configurable CLI pipeline.
5. Add optional paper-specific workflows only when the corresponding public/anonymised data are available.


## Applied AI extension

The repository includes a lightweight machine-learning screening layer for long structural-test time series: feature extraction, unsupervised anomaly detection, and robust drift scoring. These tools are framed as QA/QC and engineering-review support rather than validated autonomous damage diagnosis.
