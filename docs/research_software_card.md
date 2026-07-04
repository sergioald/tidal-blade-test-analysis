# Research software card

## Name

Tidal Blade Test Analysis

## Purpose

Process, inspect, and validate TDMS data from full-scale composite tidal blade structural-test campaigns.

## Primary scope

- First full-scale FastBlade tidal blade fatigue test
- Single-vs-multi-actuator fatigue/static comparison

## Related context

- Clamping/load-introduction studies
- Destructive/failure testing

These related studies are documented for context but are not claimed as fully reproduced by this repository.

## Users

- Research engineers processing laboratory TDMS data
- Structural testing teams checking signal quality and repeatability
- Portfolio reviewers assessing scientific Python and research-software practice

## Inputs

- TDMS files from data acquisition systems
- Test-log spreadsheets
- Optional processed CSV files for public examples and lightweight analysis
- YAML configuration files describing actuator geometry and analysis settings

## Outputs

- Channel inventories
- FFT/natural-frequency summaries
- Static load-displacement fit metrics
- Fatigue turning-point and range summaries
- Actuator/root-bending-moment checks
- QA/QC tables and plots

## Main dependencies

- Python
- NumPy
- pandas
- nptdms
- SciPy
- Matplotlib
- scikit-image
- scikit-learn
- PyWavelets

## Reproducibility approach

- Keep private raw TDMS data outside Git
- Use synthetic public examples for tests
- Provide command-line entry points
- Use `pyproject.toml` for environment metadata
- Run tests in GitHub Actions

## Risk and mitigation

| Risk | Mitigation |
|---|---|
| Raw files are too large/private for GitHub | Use ignored local `data/` folders and small synthetic examples |
| Local/private data paths | Use CLI arguments and configuration templates |
| Paper scope could be overstated | Label the first two papers as primary scope and later clamping/destructive papers as related context |


## Applied AI extension

The repository includes a lightweight machine-learning screening layer for long structural-test time series: feature extraction, unsupervised anomaly detection, and robust drift scoring. These tools are framed as QA/QC and engineering-review support rather than validated autonomous damage diagnosis.
