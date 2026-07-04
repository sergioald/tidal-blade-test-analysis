import numpy as np
import pandas as pd

from tidal_blade_test_analysis.fatigue import peak_valley_indices
from tidal_blade_test_analysis.features import cycle_response_features, rolling_window_features
from tidal_blade_test_analysis.ml import drift_zscore, fit_anomaly_detector, numeric_feature_columns


def test_rolling_window_features_returns_expected_columns():
    df = pd.DataFrame(
        {
            "time_s": np.arange(10, dtype=float),
            "load": np.arange(10, dtype=float),
            "disp": np.arange(10, dtype=float) * 2,
        }
    )
    features = rolling_window_features(
        df,
        ["load", "disp"],
        window_size=5,
        step_size=5,
        time_column="time_s",
    )
    assert len(features) == 2
    assert features.loc[0, "load__mean"] == 2.0
    assert features.loc[1, "disp__max"] == 18.0
    assert "time_centre" in features.columns


def test_cycle_response_features_uses_turning_points():
    load = np.array([0, 1, 0, -1, 0, 1, 0], dtype=float)
    displacement = 0.5 * load
    idx = peak_valley_indices(load)
    features = cycle_response_features(load, {"disp": displacement}, idx)
    assert len(features) >= 2
    assert np.all(features["load_range"] > 0)
    assert np.allclose(features["disp__range_per_load_range"], 0.5)


def test_fit_anomaly_detector_flags_synthetic_outlier():
    normal = pd.DataFrame(
        {
            "load__rms": np.ones(30),
            "disp__rms": np.ones(30) * 0.5,
            "strain__std": np.ones(30) * 0.02,
        }
    )
    outlier = pd.DataFrame({"load__rms": [3.5], "disp__rms": [2.5], "strain__std": [0.7]})
    features = pd.concat([normal, outlier], ignore_index=True)
    result = fit_anomaly_detector(features, contamination=0.05, random_state=0)
    assert result.table.loc[len(features) - 1, "is_anomaly"]
    assert result.table.loc[len(features) - 1, "anomaly_score"] < result.table["anomaly_score"].median()


def test_numeric_feature_columns_and_drift_zscore():
    reference = pd.DataFrame({"a": [1, 1, 1.1, 0.9], "b": [2, 2.1, 1.9, 2.0], "label": ["x"] * 4})
    candidate = pd.DataFrame({"a": [1.8, 1.9], "b": [2.0, 2.1], "label": ["y"] * 2})
    cols = numeric_feature_columns(reference)
    assert cols == ["a", "b"]
    scores = drift_zscore(reference, candidate, cols)
    assert scores["a"] > scores["b"]
