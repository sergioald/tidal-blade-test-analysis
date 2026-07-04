"""Utilities for tidal blade TDMS processing and structural-test analysis."""

from .actuator import (
    ActuatorSetup,
    equal_actuator_load_for_target_rbm,
    resolve_load_components,
    root_bending_moment_knm,
)
from .fatigue import cycle_ranges, peak_valley_indices
from .features import cycle_response_features, rolling_window_features
from .ml import AnomalyDetectionResult, drift_zscore, fit_anomaly_detector
from .signal import dominant_frequencies, fft_spectrum
from .static import LinearFitResult, fit_load_displacement

__all__ = [
    "ActuatorSetup",
    "AnomalyDetectionResult",
    "LinearFitResult",
    "equal_actuator_load_for_target_rbm",
    "cycle_ranges",
    "cycle_response_features",
    "dominant_frequencies",
    "drift_zscore",
    "fft_spectrum",
    "fit_load_displacement",
    "fit_anomaly_detector",
    "peak_valley_indices",
    "resolve_load_components",
    "rolling_window_features",
    "root_bending_moment_knm",
]

__version__ = "0.1.0"
