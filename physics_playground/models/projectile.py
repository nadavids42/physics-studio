"""Pure analytic and quadratic-drag projectile models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math

import numpy as np

from physics_playground.contracts import (
    AnimationData, AnimationKind, AnimationTrack, ContractResult, EventKind,
    ModelAssumption, PlotData, PlotSeries, SimulationEvent, SummaryMetric,
)
from physics_playground.serialization import to_jsonable
from physics_playground.validation import PhysicsValidationError, require_finite, require_positive
from physics_playground.performance import MAX_INTEGRATION_STEPS,MAX_TRAJECTORY_SAMPLES,enforce_budget,validate_finite_parameters


@dataclass(frozen=True, slots=True)
class ProjectileParameters:
    launch_speed_m_s: float
    launch_angle_deg: float
    gravity_m_s2: float = 9.81
    initial_height_m: float = 0.0
    mass_kg: float = 5.0
    drag_coefficient_kg_m: float = 0.0
    time_step_s: float = 0.005
    max_time_s: float = 120.0
    samples: int = 240

    def validate(self) -> None:
        validate_finite_parameters(self)
        require_positive("Launch speed", self.launch_speed_m_s)
        require_positive("Gravity", self.gravity_m_s2)
        require_positive("Mass", self.mass_kg)
        require_positive("Time step", self.time_step_s)
        require_positive("Maximum time", self.max_time_s)
        require_finite("Launch angle", self.launch_angle_deg)
        if not 0 < self.launch_angle_deg < 90:
            raise PhysicsValidationError("Launch angle must be between 0° and 90°.")
        if self.initial_height_m < 0:
            raise PhysicsValidationError("Initial height cannot be below the ground.")
        if self.drag_coefficient_kg_m < 0:
            raise PhysicsValidationError("Drag coefficient cannot be negative.")
        if self.samples < 2:
            raise PhysicsValidationError("Samples must be at least 2.")
        enforce_budget("Projectile samples",self.samples,MAX_TRAJECTORY_SAMPLES)
        enforce_budget("Projectile integration steps",math.ceil(self.max_time_s/self.time_step_s),MAX_INTEGRATION_STEPS)

    def to_dict(self) -> dict[str, object]:
        return to_jsonable(asdict(self))


@dataclass(frozen=True, slots=True)
class ProjectileResult(ContractResult[ProjectileParameters]):
    landed: bool = False
    range_m: float = 0.0
    maximum_height_m: float = 0.0
    flight_time_s: float = 0.0
    impact_speed_m_s: float | None = None


def _build_result(
    parameters: ProjectileParameters,
    time_s: np.ndarray,
    x_m: np.ndarray,
    y_m: np.ndarray,
    vx_m_s: np.ndarray,
    vy_m_s: np.ndarray,
    *,
    landed: bool,
    method: str,
) -> ProjectileResult:
    speed = np.hypot(vx_m_s, vy_m_s)
    energy = 0.5 * parameters.mass_kg * speed**2 + parameters.mass_kg * parameters.gravity_m_s2 * y_m
    range_m = float(x_m[-1])
    maximum_height = float(np.max(y_m))
    flight_time = float(time_s[-1])
    impact_speed = float(speed[-1]) if landed else None
    warnings = () if landed else ("The projectile did not reach the ground before the simulation limit.",)
    events = [SimulationEvent("launch", EventKind.START, 0.0, "Projectile launched")]
    if landed:
        events.append(SimulationEvent("impact", EventKind.COMPLETION, flight_time, "Projectile reached the ground",
                                      {"range_m": range_m, "impact_speed_m_s": impact_speed}))
    else:
        events.append(SimulationEvent("not_landed", EventKind.WARNING, flight_time, "Simulation ended before impact"))
    plots = (
        PlotData("trajectory", "Projectile trajectory", "Horizontal position (m)", "Height (m)",
                 (PlotSeries("trajectory", method, tuple(x_m), tuple(y_m)),)),
        PlotData("horizontal_time", "Horizontal position versus time", "Time (s)", "Horizontal position (m)",
                 (PlotSeries("x_time", "x(t)", tuple(time_s), tuple(x_m)),)),
        PlotData("vertical_time", "Vertical position versus time", "Time (s)", "Height (m)",
                 (PlotSeries("y_time", "y(t)", tuple(time_s), tuple(y_m)),)),
        PlotData("speed_time", "Speed versus time", "Time (s)", "Speed (m/s)",
                 (PlotSeries("speed", "speed", tuple(time_s), tuple(speed)),)),
        PlotData("energy_time", "Mechanical energy versus time", "Time (s)", "Energy (J)",
                 (PlotSeries("energy", "K + U", tuple(time_s), tuple(energy)),)),
    )
    return ProjectileResult(
        simulation_id="cannonball", parameters=parameters,
        metrics=(
            SummaryMetric("range", "Range", range_m, "m", f"{range_m:.1f} m"),
            SummaryMetric("maximum_height", "Maximum height", maximum_height, "m", f"{maximum_height:.1f} m"),
            SummaryMetric("flight_time", "Flight time", flight_time, "s", f"{flight_time:.2f} s"),
            SummaryMetric("impact_speed", "Impact speed", impact_speed or 0.0, "m/s",
                          f"{impact_speed:.1f} m/s" if impact_speed is not None else "Not landed"),
            SummaryMetric("energy_lost", "Mechanical energy lost", max(0.0, float(energy[0]-energy[-1])), "J"),
        ),
        events=tuple(events), plots=plots,
        animation=AnimationData(AnimationKind.TWO_DIMENSIONAL, tuple(time_s),
                                (AnimationTrack("projectile", "Cannonball", tuple(x_m), tuple(y_m)),),
                                3_200, {"x_min": 0.0, "x_max": max(1.0, range_m*1.12),
                                        "y_min": 0.0, "y_max": max(1.0, maximum_height*1.25)}),
        assumptions=(
            ModelAssumption("flat_ground", "Launch and landing ground are flat and stationary."),
            ModelAssumption("constant_gravity", "Gravity is uniform and points straight down."),
            ModelAssumption("point_projectile", "The cannonball is treated as a point mass."),
        ), completed=landed, warnings=warnings, landed=landed, range_m=range_m,
        maximum_height_m=maximum_height, flight_time_s=flight_time, impact_speed_m_s=impact_speed,
    )


def simulate_no_drag(parameters: ProjectileParameters) -> ProjectileResult:
    """Analytic projectile solution with no air resistance."""

    parameters.validate()
    theta = math.radians(parameters.launch_angle_deg)
    vx = parameters.launch_speed_m_s * math.cos(theta)
    vy = parameters.launch_speed_m_s * math.sin(theta)
    discriminant = vy**2 + 2 * parameters.gravity_m_s2 * parameters.initial_height_m
    flight_time = (vy + math.sqrt(discriminant)) / parameters.gravity_m_s2
    time_s = np.linspace(0.0, flight_time, parameters.samples)
    x_m = vx * time_s
    y_m = parameters.initial_height_m + vy*time_s - 0.5*parameters.gravity_m_s2*time_s**2
    y_m[-1] = 0.0
    return _build_result(parameters, time_s, x_m, y_m,
                         np.full_like(time_s, vx), vy-parameters.gravity_m_s2*time_s,
                         landed=True, method="No drag (analytic)")


def _derivative(state: np.ndarray, parameters: ProjectileParameters) -> np.ndarray:
    _, _, vx, vy = state
    speed = math.hypot(vx, vy)
    factor = parameters.drag_coefficient_kg_m / parameters.mass_kg
    return np.array((vx, vy, -factor*speed*vx, -parameters.gravity_m_s2-factor*speed*vy), dtype=float)


def _rk4(state: np.ndarray, dt: float, parameters: ProjectileParameters) -> np.ndarray:
    k1 = _derivative(state, parameters)
    k2 = _derivative(state + 0.5*dt*k1, parameters)
    k3 = _derivative(state + 0.5*dt*k2, parameters)
    k4 = _derivative(state + dt*k3, parameters)
    return state + dt*(k1+2*k2+2*k3+k4)/6


def simulate_quadratic_drag(parameters: ProjectileParameters) -> ProjectileResult:
    """Integrate quadratic drag with RK4 and interpolate the exact ground crossing."""

    parameters.validate()
    theta = math.radians(parameters.launch_angle_deg)
    state = np.array((0.0, parameters.initial_height_m,
                      parameters.launch_speed_m_s*math.cos(theta),
                      parameters.launch_speed_m_s*math.sin(theta)), dtype=float)
    states = [state.copy()]
    times = [0.0]
    landed = False
    while times[-1] < parameters.max_time_s:
        dt = min(parameters.time_step_s, parameters.max_time_s-times[-1])
        next_state = _rk4(state, dt, parameters)
        next_time = times[-1] + dt
        if next_state[1] <= 0 and next_time > 0:
            denominator = state[1] - next_state[1]
            fraction = state[1] / denominator if denominator > 0 else 1.0
            impact = state + fraction*(next_state-state)
            impact[1] = 0.0
            states.append(impact); times.append(times[-1]+fraction*dt); landed=True; break
        states.append(next_state.copy()); times.append(next_time); state = next_state
    array = np.asarray(states)
    return _build_result(parameters, np.asarray(times), array[:,0], array[:,1], array[:,2], array[:,3],
                         landed=landed, method="Quadratic drag (RK4)")


def simulate_projectile(parameters: ProjectileParameters) -> ProjectileResult:
    return simulate_no_drag(parameters) if parameters.drag_coefficient_kg_m == 0 else simulate_quadratic_drag(parameters)


@lru_cache(maxsize=128)
def projectile_range_scan(speed_m_s:float,gravity_m_s2:float,start_angle:int=5,end_angle:int=89):
    angles=tuple(range(start_angle,end_angle+1))
    ranges=tuple(simulate_no_drag(ProjectileParameters(speed_m_s,float(angle),gravity_m_s2)).range_m for angle in angles)
    return angles,ranges
