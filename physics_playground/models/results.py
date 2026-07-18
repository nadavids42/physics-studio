"""Typed result models for numerical and analytic simulations."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class Trajectory:
    time_s: FloatArray
    channels: Mapping[str, FloatArray]

    def __post_init__(self) -> None:
        time_s = np.asarray(self.time_s, dtype=float)
        channels = {name: np.asarray(values, dtype=float) for name, values in self.channels.items()}
        object.__setattr__(self, "time_s", time_s)
        object.__setattr__(self, "channels", MappingProxyType(channels))


@dataclass(frozen=True, slots=True)
class ScalarMetrics:
    values: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))


@dataclass(frozen=True, slots=True)
class SimulationResult:
    trajectory: Trajectory
    metrics: ScalarMetrics = field(default_factory=ScalarMetrics)
    completed: bool = True
    message: str | None = None


@dataclass(frozen=True, slots=True)
class IntegrationResult(SimulationResult):
    method: str = "unknown"
    step_size_s: float | None = None


@dataclass(frozen=True, slots=True)
class OrbitResult(IntegrationResult):
    outcome: str = "unknown"
    eccentricity: float | None = None
    energy_drift: float | None = None


@dataclass(frozen=True, slots=True)
class CollisionResult(SimulationResult):
    collision_time_s: float | None = None
    final_velocity_1_m_s: float = 0.0
    final_velocity_2_m_s: float = 0.0
