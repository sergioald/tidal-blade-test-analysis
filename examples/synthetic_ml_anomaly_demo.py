"""Synthetic anomaly-screening example for tidal blade fatigue data.

Run from the repository root with:

    python examples/synthetic_ml_anomaly_demo.py

This example uses synthetic signals only. It demonstrates how to extract
fixed-window features and fit a transparent baseline anomaly detector without
shipping private TDMS files.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from tidal_blade_test_analysis.features import rolling_window_features
from tidal_blade_test_analysis.ml import fit_anomaly_detector

rng = np.random.default_rng(7)
sample_rate_hz = 50
duration_s = 120
time_s = np.arange(0, duration_s, 1 / sample_rate_hz)

# Synthetic actuator load and blade response.
load_kn = 100 + 45 * np.sin(2 * np.pi * 1.0 * time_s) + rng.normal(0, 1.2, len(time_s))
displacement_mm = 0.18 * load_kn + rng.normal(0, 0.4, len(time_s))
strain_microstrain = -2.8 * load_kn + rng.normal(0, 8.0, len(time_s))

# Inject a short control/sensor anomaly.
anomaly_mask = (time_s > 72) & (time_s < 78)
displacement_mm[anomaly_mask] += 14 * np.sin(2 * np.pi * 8 * time_s[anomaly_mask])
strain_microstrain[anomaly_mask] += 180

signals = pd.DataFrame(
    {
        "time_s": time_s,
        "load_kn": load_kn,
        "displacement_mm": displacement_mm,
        "strain_microstrain": strain_microstrain,
    }
)
features = rolling_window_features(
    signals,
    ["load_kn", "displacement_mm", "strain_microstrain"],
    window_size=sample_rate_hz * 2,
    step_size=sample_rate_hz,
    time_column="time_s",
)
result = fit_anomaly_detector(features, contamination=0.05, random_state=7)
ranked = result.table.sort_values("anomaly_score").head(8)
print(ranked[["time_centre", "anomaly_score", "is_anomaly"]].to_string(index=False))
