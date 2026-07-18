"""Pure ideal, damped, and driven mass-spring oscillator models."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from functools import lru_cache

import numpy as np

from physics_playground.contracts import (
    AnimationData,
    AnimationKind,
    AnimationTrack,
    ContractResult,
    EventKind,
    ModelAssumption,
    PlotData,
    PlotKind,
    PlotSeries,
    SimulationEvent,
    SummaryMetric,
)
from physics_playground.performance import (
    MAX_SCAN_POINTS,
    MAX_TRAJECTORY_SAMPLES,
    enforce_budget,
    validate_finite_parameters,
)
from physics_playground.serialization import to_jsonable
from physics_playground.validation import PhysicsValidationError, require_positive


@dataclass(frozen=True, slots=True)
class SpringParameters:
    mass_kg: float
    stiffness_n_m: float
    initial_displacement_m: float
    damping_n_s_m: float = 0.0
    drive_force_n: float = 0.0
    drive_frequency_ratio: float = 1.0
    duration_s: float = 20.0
    samples: int = 600

    @property
    def natural_angular_frequency_rad_s(self) -> float:
        return math.sqrt(self.stiffness_n_m / self.mass_kg)

    @property
    def natural_frequency_hz(self) -> float:
        return self.natural_angular_frequency_rad_s / (2 * math.pi)

    @property
    def period_s(self) -> float:
        return 2 * math.pi / self.natural_angular_frequency_rad_s

    @property
    def drive_angular_frequency_rad_s(self) -> float:
        return self.drive_frequency_ratio * self.natural_angular_frequency_rad_s

    def validate(self) -> None:
        validate_finite_parameters(self)
        require_positive("Mass", self.mass_kg)
        require_positive("Spring stiffness", self.stiffness_n_m)
        require_positive("Starting displacement", abs(self.initial_displacement_m))
        require_positive("Duration", self.duration_s)
        if self.damping_n_s_m < 0:
            raise PhysicsValidationError("Damping cannot be negative.")
        if self.drive_force_n < 0:
            raise PhysicsValidationError("Driving force cannot be negative.")
        if self.drive_frequency_ratio <= 0:
            raise PhysicsValidationError("Driving frequency ratio must be positive.")
        if self.samples < 3:
            raise PhysicsValidationError("Samples must be at least 3.")
        enforce_budget("Spring samples", self.samples, MAX_TRAJECTORY_SAMPLES)

    def to_dict(self) -> dict[str, object]:
        return to_jsonable(asdict(self))


@dataclass(frozen=True, slots=True)
class SpringResult(ContractResult[SpringParameters]):
    natural_frequency_hz: float = 0.0
    natural_angular_frequency_rad_s: float = 0.0
    period_s: float = 0.0
    maximum_speed_m_s: float = 0.0
    late_response_amplitude_m: float = 0.0


def _result(
    p: SpringParameters, t: np.ndarray, x: np.ndarray, v: np.ndarray, method: str
) -> SpringResult:
    energy = 0.5 * p.mass_kg * v**2 + 0.5 * p.stiffness_n_m * x**2
    late = float(np.max(np.abs(x[len(x) // 2 :])))
    plots = (
        PlotData(
            "position_time",
            "Position versus time",
            "Time (s)",
            "Position (m)",
            (PlotSeries("position", "x(t)", tuple(t), tuple(x)),),
        ),
        PlotData(
            "velocity_time",
            "Velocity versus time",
            "Time (s)",
            "Velocity (m/s)",
            (PlotSeries("velocity", "v(t)", tuple(t), tuple(v)),),
        ),
        PlotData(
            "energy_time",
            "Mechanical energy versus time",
            "Time (s)",
            "Energy (J)",
            (PlotSeries("energy", "E(t)", tuple(t), tuple(energy)),),
        ),
        PlotData(
            "phase_space",
            "Phase space",
            "Position (m)",
            "Velocity (m/s)",
            (PlotSeries("phase", "(x,v)", tuple(x), tuple(v)),),
            PlotKind.PHASE,
        ),
    )
    return SpringResult(
        simulation_id="boing",
        parameters=p,
        metrics=(
            SummaryMetric("period", "Natural period", p.period_s, "s", f"{p.period_s:.2f} s"),
            SummaryMetric(
                "natural_frequency",
                "Natural frequency",
                p.natural_frequency_hz,
                "Hz",
                f"{p.natural_frequency_hz:.3f} Hz",
            ),
            SummaryMetric(
                "natural_angular_frequency",
                "Natural angular frequency",
                p.natural_angular_frequency_rad_s,
                "rad/s",
                f"{p.natural_angular_frequency_rad_s:.2f} rad/s",
            ),
            SummaryMetric(
                "maximum_speed",
                "Maximum speed",
                float(np.max(np.abs(v))),
                "m/s",
                f"{np.max(np.abs(v)):.2f} m/s",
            ),
            SummaryMetric("late_amplitude", "Late response amplitude", late, "m", f"{late:.2f} m"),
        ),
        events=(
            SimulationEvent("release", EventKind.START, 0, "Mass released"),
            SimulationEvent("complete", EventKind.COMPLETION, float(t[-1]), "Oscillation complete"),
        ),
        plots=plots,
        animation=AnimationData(
            AnimationKind.ONE_DIMENSIONAL,
            tuple(t),
            (AnimationTrack("mass", "Spring mass", tuple(x), style={"color": "#EF5350"}),),
            4200,
            {"minimum": float(np.min(x) * 1.25 - 0.2), "maximum": float(np.max(x) * 1.25 + 0.2)},
        ),
        assumptions=(
            ModelAssumption("hooke", "The spring obeys Hooke's law F=-kx."),
            ModelAssumption("point_mass", "The mass is a point and the spring is massless."),
            ModelAssumption("linear_damping", "Damping is proportional to velocity."),
        ),
        natural_frequency_hz=p.natural_frequency_hz,
        natural_angular_frequency_rad_s=p.natural_angular_frequency_rad_s,
        period_s=p.period_s,
        maximum_speed_m_s=float(np.max(np.abs(v))),
        late_response_amplitude_m=late,
    )


def simulate_undamped(p: SpringParameters) -> SpringResult:
    p.validate()
    omega = p.natural_angular_frequency_rad_s
    t = np.linspace(0, p.duration_s, p.samples)
    x = p.initial_displacement_m * np.cos(omega * t)
    v = -p.initial_displacement_m * omega * np.sin(omega * t)
    return _result(p, t, x, v, "Analytic ideal SHM")


def _rhs(state: np.ndarray, time: float, p: SpringParameters) -> np.ndarray:
    x, v = state
    force = p.drive_force_n * math.cos(p.drive_angular_frequency_rad_s * time)
    return np.array((v, (force - p.stiffness_n_m * x - p.damping_n_s_m * v) / p.mass_kg))


def simulate_damped_driven(p: SpringParameters) -> SpringResult:
    p.validate()
    t = np.linspace(0, p.duration_s, p.samples)
    dt = t[1] - t[0]
    states = np.zeros((p.samples, 2))
    states[0] = (p.initial_displacement_m, 0)
    for i in range(1, p.samples):
        state = states[i - 1]
        ti = t[i - 1]
        k1 = _rhs(state, ti, p)
        k2 = _rhs(state + dt * k1 / 2, ti + dt / 2, p)
        k3 = _rhs(state + dt * k2 / 2, ti + dt / 2, p)
        k4 = _rhs(state + dt * k3, ti + dt, p)
        states[i] = state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return _result(p, t, states[:, 0], states[:, 1], "RK4 damped/driven oscillator")


def simulate_spring(p: SpringParameters) -> SpringResult:
    return (
        simulate_undamped(p)
        if p.damping_n_s_m == 0 and p.drive_force_n == 0
        else simulate_damped_driven(p)
    )


@lru_cache(maxsize=128)
def resonance_sweep(
    mass_kg: float,
    stiffness_n_m: float,
    damping_n_s_m: float,
    drive_force_n: float,
    duration_s: float = 40.0,
    points: int = 41,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    enforce_budget("Resonance sweep points", points, MAX_SCAN_POINTS)
    ratios = np.linspace(0.2, 2.2, points)
    amplitudes = []
    for ratio in ratios:
        p = SpringParameters(
            mass_kg,
            stiffness_n_m,
            0.01,
            damping_n_s_m,
            drive_force_n,
            float(ratio),
            duration_s,
            1000,
        )
        amplitudes.append(simulate_damped_driven(p).late_response_amplitude_m)
    return tuple(ratios), tuple(amplitudes)
