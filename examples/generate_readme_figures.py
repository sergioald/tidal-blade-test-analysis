"""Generate synthetic README figures without using private TDMS data.

The examples are deliberately small and synthetic. They show the public
analysis workflow rather than reproducing private experimental results.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tidal_blade_test_analysis.features import rolling_window_features
from tidal_blade_test_analysis.ml import fit_anomaly_detector
from tidal_blade_test_analysis.static import fit_load_displacement

ASSET_DIR = Path(__file__).resolve().parents[1] / "docs" / "assets"
ASSET_DIR.mkdir(parents=True, exist_ok=True)


def save_static_fit() -> None:
    """Create a synthetic static load-displacement fit figure."""
    rng = np.random.default_rng(7)
    displacement_mm = np.linspace(0, 155, 140)
    load_kn = 1.83 * displacement_mm + 4.0 + rng.normal(0, 4.2, size=displacement_mm.size)
    fit = fit_load_displacement(load_kn, displacement_mm)
    predicted = fit.predict(displacement_mm)

    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.scatter(displacement_mm, load_kn, s=14, alpha=0.75, label="Synthetic samples")
    ax.plot(displacement_mm, predicted, linewidth=2, label=f"Linear fit, R² = {fit.r2:.3f}")
    ax.set_title("Static load-displacement check")
    ax.set_xlabel("Displacement (mm)")
    ax.set_ylabel("Load (kN)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.savefig(ASSET_DIR / "static_fit_example.png", dpi=180)
    plt.close(fig)


def save_fatigue_cycle_summary() -> None:
    """Create a synthetic fatigue-cycle load-range summary figure."""
    rng = np.random.default_rng(11)
    cycle_id = np.arange(1, 65)
    slow_drift = np.linspace(0.0, -4.0, cycle_id.size)
    cycle_ranges = 145 + slow_drift + rng.normal(0, 2.0, cycle_id.size)
    cycle_ranges[42:48] -= np.linspace(4, 9, 6)

    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.plot(cycle_id, cycle_ranges, marker="o", markersize=4, linewidth=1.5)
    ax.axhline(np.mean(cycle_ranges), linestyle="--", linewidth=1.5, label="Mean range")
    ax.set_title("Fatigue-cycle load-range summary")
    ax.set_xlabel("Cycle segment")
    ax.set_ylabel("Peak-to-trough range (kN)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.savefig(ASSET_DIR / "fatigue_cycle_summary.png", dpi=180)
    plt.close(fig)


def save_anomaly_screening() -> None:
    """Create a synthetic applied-AI anomaly-screening figure."""
    rng = np.random.default_rng(23)
    sample_rate_hz = 100
    time_s = np.arange(0, 120, 1 / sample_rate_hz)
    load_kn = 110 + 70 * np.sin(2 * np.pi * 0.5 * time_s) + rng.normal(0, 1.8, time_s.size)
    displacement_mm = 0.42 * load_kn + rng.normal(0, 1.5, time_s.size)
    strain_microstrain = 4.8 * load_kn + rng.normal(0, 18, time_s.size)

    anomaly_mask = (time_s > 68) & (time_s < 78)
    displacement_mm[anomaly_mask] += np.linspace(0, 18, anomaly_mask.sum())
    strain_microstrain[anomaly_mask] += 70 * np.sin(np.linspace(0, 5 * np.pi, anomaly_mask.sum()))

    signals = pd.DataFrame(
        {
            "time_s": time_s,
            "load_kn": load_kn,
            "tip_displacement_mm": displacement_mm,
            "strain_microstrain": strain_microstrain,
        }
    )
    features = rolling_window_features(
        signals,
        ["load_kn", "tip_displacement_mm", "strain_microstrain"],
        window_size=500,
        step_size=250,
        time_column="time_s",
    )
    result = fit_anomaly_detector(features, contamination=0.08)
    table = result.table

    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.plot(signals["time_s"], signals["tip_displacement_mm"], linewidth=1.0, label="Synthetic displacement")
    flagged = table[table["is_anomaly"]]
    for _, row in flagged.iterrows():
        ax.axvspan(row["time_start"], row["time_stop"], alpha=0.16)
    ax.set_title("Applied-AI screening on synthetic fatigue data")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tip displacement (mm)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.savefig(ASSET_DIR / "anomaly_screening_demo.png", dpi=180)
    plt.close(fig)


def main() -> None:
    save_static_fit()
    save_fatigue_cycle_summary()
    save_anomaly_screening()
    print(f"Figures written to {ASSET_DIR}")


if __name__ == "__main__":
    main()
