# Applied AI and machine-learning extension

This repository includes a lightweight applied-AI layer for exploratory screening of tidal blade structural-test data. The goal is to support engineering review, not to replace it.

## What is included

- Fixed-window feature extraction for actuator loads, displacement, strain, root bending moment, pressure, or other processed channels.
- Cycle/turning-point response features for fatigue tests.
- A baseline unsupervised anomaly detector using robust scaling and Isolation Forest.
- Robust drift scores for comparing one section of a test against a reference section.
- A synthetic example that can run without private TDMS data.

## Why this is useful

For long fatigue tests, the raw time series are large and difficult to inspect manually. Feature-based screening can help prioritise regions where the response becomes unusual, for example:

- control overshoot or undershoot,
- actuator/load-cell timing issues,
- sensor dropouts or clipping,
- changes in displacement/load or strain/load relationships,
- unusual windows before or after manual interventions.

## Responsible interpretation

The anomaly labels are **screening flags**, not confirmed damage labels. A flagged window should be checked against the raw signal, test log, actuator state, sensor health, environmental conditions, and engineering judgement. This is especially important because unusual behaviour can be caused by control-system tuning, sensor artefacts, saddle effects, temperature variation, or real structural change.

## Minimal example

```python
import pandas as pd
from tidal_blade_test_analysis.features import rolling_window_features
from tidal_blade_test_analysis.ml import fit_anomaly_detector

signals = pd.read_csv("data/processed/fatigue_channels.csv")
features = rolling_window_features(
    signals,
    ["actuator_load_kn", "tip_displacement_mm", "strain_1_1_microstrain"],
    window_size=5000,
    step_size=2500,
    time_column="time_s",
)
result = fit_anomaly_detector(features, contamination=0.02)
result.table.to_csv("data/results/ml/anomaly_scores.csv", index=False)
```

## Synthetic demonstration

```bash
python examples/synthetic_ml_anomaly_demo.py
```

The demo creates synthetic fatigue-like load, displacement, and strain channels, injects a short anomaly, extracts window features, and prints the most unusual windows.
