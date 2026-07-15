"""Reusable validation for model boundaries and trajectory contracts."""

from collections.abc import Mapping
import math

import numpy as np
from numpy.typing import ArrayLike


class PhysicsValidationError(ValueError):
    """Raised when a simulation receives physically or numerically invalid input."""


def require_finite(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise PhysicsValidationError(f"{name} must be finite.")
    return value


def require_positive(name: str, value: float) -> float:
    require_finite(name, value)
    if value <= 0:
        raise PhysicsValidationError(f"{name} must be greater than zero.")
    return value


def require_between(name: str, value: float, minimum: float, maximum: float) -> float:
    require_finite(name, value)
    if not minimum <= value <= maximum:
        raise PhysicsValidationError(f"{name} must be between {minimum} and {maximum}.")
    return value


def validate_trajectory(time_s: ArrayLike, channels: Mapping[str, ArrayLike]) -> None:
    time_array = np.asarray(time_s, dtype=float)
    if time_array.ndim != 1 or time_array.size == 0:
        raise PhysicsValidationError("Trajectory time must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(time_array)):
        raise PhysicsValidationError("Trajectory time contains non-finite values.")
    if np.any(np.diff(time_array) < 0):
        raise PhysicsValidationError("Trajectory time must be non-decreasing.")
    for name, values in channels.items():
        array = np.asarray(values, dtype=float)
        if array.shape != time_array.shape:
            raise PhysicsValidationError(f"Channel {name!r} must match the time array shape.")
        if not np.all(np.isfinite(array)):
            raise PhysicsValidationError(f"Channel {name!r} contains non-finite values.")
