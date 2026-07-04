"""Actuator-geometry helpers for tidal blade structural tests.

The functions in this module intentionally keep the mechanics simple and
transparent: they are intended for configuration checks, quick summaries, and
unit tests around point-load actuator setups. Detailed beam/FE modelling remains
outside the scope of this public repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import numpy as np


@dataclass(frozen=True)
class ActuatorSetup:
    """Point-load actuator setup measured from the blade root.

    Parameters
    ----------
    positions_m:
        Actuator contact-point distances from the blade root, in metres.
    angle_deg_from_xb:
        Optional load angle from the blade XB axis. Positive values are treated
        as a rotation from XB towards YB.
    name:
        Optional human-readable setup name.
    """

    positions_m: tuple[float, ...]
    angle_deg_from_xb: float = 0.0
    name: str = ""

    @classmethod
    def from_positions(
        cls,
        positions_m: list[float] | tuple[float, ...],
        *,
        angle_deg_from_xb: float = 0.0,
        name: str = "",
    ) -> ActuatorSetup:
        positions = tuple(float(value) for value in positions_m)
        _validate_positions(positions)
        return cls(positions_m=positions, angle_deg_from_xb=float(angle_deg_from_xb), name=name)

    @property
    def actuator_count(self) -> int:
        return len(self.positions_m)

    def root_bending_moment(self, loads_kn: list[float] | tuple[float, ...] | np.ndarray) -> float:
        """Return root bending moment in kN m from actuator loads in kN."""
        return root_bending_moment_knm(loads_kn, self.positions_m)

    def equal_load_for_target_rbm(self, target_rbm_knm: float) -> float:
        """Return equal load per actuator needed to match a target root moment."""
        return equal_actuator_load_for_target_rbm(target_rbm_knm, self.positions_m)


def _validate_positions(positions_m: tuple[float, ...] | np.ndarray) -> None:
    if len(positions_m) == 0:
        raise ValueError("At least one actuator position is required")
    values = np.asarray(positions_m, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("Actuator positions must be finite")
    if np.any(values <= 0):
        raise ValueError("Actuator positions must be positive distances from the root")


def _as_loads_and_positions(
    loads_kn: list[float] | tuple[float, ...] | np.ndarray,
    positions_m: list[float] | tuple[float, ...] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    loads = np.asarray(loads_kn, dtype=float)
    positions = np.asarray(positions_m, dtype=float)
    if loads.ndim != 1 or positions.ndim != 1:
        raise ValueError("loads_kn and positions_m must be one-dimensional")
    if len(loads) != len(positions):
        raise ValueError("loads_kn and positions_m must have the same length")
    if len(loads) == 0:
        raise ValueError("At least one load/position pair is required")
    if not np.all(np.isfinite(loads)) or not np.all(np.isfinite(positions)):
        raise ValueError("loads_kn and positions_m must contain finite values")
    _validate_positions(tuple(float(value) for value in positions))
    return loads, positions


def root_bending_moment_knm(
    loads_kn: list[float] | tuple[float, ...] | np.ndarray,
    positions_m: list[float] | tuple[float, ...] | np.ndarray,
) -> float:
    """Compute root bending moment from point loads.

    The convention is ``sum(load_kN * distance_m)``. The sign of the load is
    preserved, so use absolute values before calling when a magnitude-only check
    is required.
    """
    loads, positions = _as_loads_and_positions(loads_kn, positions_m)
    return float(np.sum(loads * positions))


def equal_actuator_load_for_target_rbm(
    target_rbm_knm: float,
    positions_m: list[float] | tuple[float, ...] | np.ndarray,
) -> float:
    """Return equal actuator load in kN for a desired root bending moment."""
    positions = np.asarray(positions_m, dtype=float)
    _validate_positions(tuple(float(value) for value in positions))
    if not np.isfinite(target_rbm_knm):
        raise ValueError("target_rbm_knm must be finite")
    return float(target_rbm_knm / np.sum(positions))


def resolve_load_components(load_kn: float, angle_deg_from_xb: float) -> tuple[float, float]:
    """Resolve a load into XB and YB components.

    Returns
    -------
    tuple[float, float]
        ``(load_xb_kn, load_yb_kn)``.
    """
    if not np.isfinite(load_kn) or not np.isfinite(angle_deg_from_xb):
        raise ValueError("load_kn and angle_deg_from_xb must be finite")
    angle = radians(float(angle_deg_from_xb))
    return float(load_kn * cos(angle)), float(load_kn * sin(angle))
