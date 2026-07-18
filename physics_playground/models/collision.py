"""Pure one-dimensional collision model used by Bumper Cars.

No Streamlit, Matplotlib, or canvas code belongs in this module. The model is
deterministic and can be reused by tests, notebooks, or other user interfaces.
"""

from __future__ import annotations

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
    PlotSeries,
    SimulationEvent,
    SummaryMetric,
)
from physics_playground.performance import (
    MAX_TRAJECTORY_SAMPLES,
    enforce_budget,
    validate_finite_parameters,
)
from physics_playground.serialization import to_jsonable
from physics_playground.validation import (
    PhysicsValidationError,
    require_between,
    require_finite,
    require_positive,
)


@dataclass(frozen=True, slots=True)
class CollisionParameters:
    """Inputs for two cars moving along one dimension."""

    mass_a_kg: float
    mass_b_kg: float
    velocity_a_m_s: float
    velocity_b_m_s: float
    restitution: float
    initial_position_a_m: float = -6.0
    initial_position_b_m: float = 6.0
    contact_distance_m: float = 0.8
    aftermath_time_s: float = 3.0
    samples: int = 300

    def validate(self) -> None:
        validate_finite_parameters(self)
        require_positive("Car A mass", self.mass_a_kg)
        require_positive("Car B mass", self.mass_b_kg)
        require_finite("Car A velocity", self.velocity_a_m_s)
        require_finite("Car B velocity", self.velocity_b_m_s)
        require_between("Restitution", self.restitution, 0.0, 1.0)
        require_positive("Contact distance", self.contact_distance_m)
        require_positive("Aftermath time", self.aftermath_time_s)
        if self.samples < 2:
            raise PhysicsValidationError("Animation samples must be at least 2.")
        enforce_budget("Collision samples", self.samples, MAX_TRAJECTORY_SAMPLES)
        gap = self.initial_position_b_m - self.initial_position_a_m - self.contact_distance_m
        if gap < 0:
            raise PhysicsValidationError(
                "The cars start overlapped. Move Car B farther to the right."
            )

    def to_dict(self) -> dict[str, object]:
        return to_jsonable(asdict(self))


@dataclass(frozen=True, slots=True)
class VelocitySnapshot:
    car_a_m_s: float
    car_b_m_s: float


@dataclass(frozen=True, slots=True)
class CollisionDiagnostics:
    momentum_before_kg_m_s: float
    momentum_after_kg_m_s: float
    kinetic_energy_before_j: float
    kinetic_energy_after_j: float
    energy_lost_j: float
    center_of_mass_velocity_m_s: float


@dataclass(frozen=True, slots=True)
class CollisionResult(ContractResult[CollisionParameters]):
    velocities_before: VelocitySnapshot = VelocitySnapshot(0.0, 0.0)
    velocities_after: VelocitySnapshot = VelocitySnapshot(0.0, 0.0)
    diagnostics: CollisionDiagnostics = CollisionDiagnostics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    collision_time_s: float | None = None
    collided: bool = False


def post_collision_velocities(parameters: CollisionParameters) -> VelocitySnapshot:
    """Return the velocities implied by momentum and restitution equations."""

    parameters.validate()
    m_a, m_b = parameters.mass_a_kg, parameters.mass_b_kg
    v_a, v_b = parameters.velocity_a_m_s, parameters.velocity_b_m_s
    e = parameters.restitution
    after_a = v_a - (1.0 + e) * m_b * (v_a - v_b) / (m_a + m_b)
    after_b = v_b + (1.0 + e) * m_a * (v_a - v_b) / (m_a + m_b)
    return VelocitySnapshot(after_a, after_b)


def collision_time(parameters: CollisionParameters) -> float | None:
    """Return first contact time, or ``None`` when separation never closes."""

    parameters.validate()
    gap = (
        parameters.initial_position_b_m
        - parameters.initial_position_a_m
        - parameters.contact_distance_m
    )
    closing_speed = parameters.velocity_a_m_s - parameters.velocity_b_m_s
    if closing_speed <= 0.0:
        return None
    return gap / closing_speed


def _diagnostics(
    parameters: CollisionParameters,
    after: VelocitySnapshot,
) -> CollisionDiagnostics:
    m_a, m_b = parameters.mass_a_kg, parameters.mass_b_kg
    v_a, v_b = parameters.velocity_a_m_s, parameters.velocity_b_m_s
    momentum_before = m_a * v_a + m_b * v_b
    momentum_after = m_a * after.car_a_m_s + m_b * after.car_b_m_s
    energy_before = 0.5 * m_a * v_a**2 + 0.5 * m_b * v_b**2
    energy_after = 0.5 * m_a * after.car_a_m_s**2 + 0.5 * m_b * after.car_b_m_s**2
    return CollisionDiagnostics(
        momentum_before,
        momentum_after,
        energy_before,
        energy_after,
        max(0.0, energy_before - energy_after),
        momentum_before / (m_a + m_b),
    )


def simulate_collision(parameters: CollisionParameters) -> CollisionResult:
    """Simulate positions before and after an instantaneous collision.

    A non-closing pair is returned as a valid ``collided=False`` result so a UI
    can explain the setup without using exceptions for an expected outcome.
    """

    parameters.validate()
    impact_time = collision_time(parameters)
    before = VelocitySnapshot(parameters.velocity_a_m_s, parameters.velocity_b_m_s)
    after = post_collision_velocities(parameters) if impact_time is not None else before
    total_time = (
        impact_time + parameters.aftermath_time_s
        if impact_time is not None
        else parameters.aftermath_time_s * 2.0
    )
    time_s = np.linspace(0.0, total_time, parameters.samples)

    if impact_time is None:
        position_a = parameters.initial_position_a_m + before.car_a_m_s * time_s
        position_b = parameters.initial_position_b_m + before.car_b_m_s * time_s
    else:
        impact_a = parameters.initial_position_a_m + before.car_a_m_s * impact_time
        impact_b = parameters.initial_position_b_m + before.car_b_m_s * impact_time
        position_a = np.where(
            time_s <= impact_time,
            parameters.initial_position_a_m + before.car_a_m_s * time_s,
            impact_a + after.car_a_m_s * (time_s - impact_time),
        )
        position_b = np.where(
            time_s <= impact_time,
            parameters.initial_position_b_m + before.car_b_m_s * time_s,
            impact_b + after.car_b_m_s * (time_s - impact_time),
        )

    diagnostics = _diagnostics(parameters, after)
    events = [SimulationEvent("start", EventKind.START, 0.0, "Cars begin moving")]
    warnings: tuple[str, ...] = ()
    if impact_time is None:
        events.append(
            SimulationEvent(
                "no_collision",
                EventKind.WARNING,
                0.0,
                "The cars never collide",
                {"closing_speed_m_s": before.car_a_m_s - before.car_b_m_s},
            )
        )
        warnings = ("Car A is not catching Car B, so the cars never touch.",)
    else:
        events.extend(
            (
                SimulationEvent(
                    "impact",
                    EventKind.COLLISION,
                    impact_time,
                    "The bumpers make contact",
                    {
                        "position_a_m": float(np.interp(impact_time, time_s, position_a)),
                        "position_b_m": float(np.interp(impact_time, time_s, position_b)),
                        "restitution": parameters.restitution,
                    },
                ),
                SimulationEvent(
                    "complete", EventKind.COMPLETION, total_time, "Collision aftermath complete"
                ),
            )
        )

    minimum = float(min(np.min(position_a), np.min(position_b)) - 1.5)
    maximum = float(max(np.max(position_a), np.max(position_b)) + 1.5)
    metrics = (
        SummaryMetric(
            "velocity_a_after", "Car A after", after.car_a_m_s, "m/s", f"{after.car_a_m_s:.2f} m/s"
        ),
        SummaryMetric(
            "velocity_b_after", "Car B after", after.car_b_m_s, "m/s", f"{after.car_b_m_s:.2f} m/s"
        ),
        SummaryMetric(
            "momentum_before", "Momentum before", diagnostics.momentum_before_kg_m_s, "kg·m/s"
        ),
        SummaryMetric(
            "momentum_after", "Momentum after", diagnostics.momentum_after_kg_m_s, "kg·m/s"
        ),
        SummaryMetric(
            "kinetic_energy_before",
            "Kinetic energy before",
            diagnostics.kinetic_energy_before_j,
            "J",
        ),
        SummaryMetric(
            "kinetic_energy_after", "Kinetic energy after", diagnostics.kinetic_energy_after_j, "J"
        ),
        SummaryMetric("energy_lost", "Energy lost", diagnostics.energy_lost_j, "J"),
        SummaryMetric(
            "center_of_mass_velocity",
            "Center-of-mass velocity",
            diagnostics.center_of_mass_velocity_m_s,
            "m/s",
        ),
    )
    return CollisionResult(
        simulation_id="bumper_cars",
        parameters=parameters,
        metrics=metrics,
        events=tuple(events),
        plots=(
            PlotData(
                "positions",
                "Straight lines, then a kink at impact",
                "Time (s)",
                "Position (m)",
                (
                    PlotSeries("car_a", "Car A", tuple(time_s), tuple(position_a), "tab:blue"),
                    PlotSeries("car_b", "Car B", tuple(time_s), tuple(position_b), "tab:orange"),
                ),
            ),
        ),
        animation=AnimationData(
            AnimationKind.ONE_DIMENSIONAL,
            tuple(time_s),
            (
                AnimationTrack("car_a", "Car A", tuple(position_a), style={"color": "#42A5F5"}),
                AnimationTrack("car_b", "Car B", tuple(position_b), style={"color": "#FF8A65"}),
            ),
            4_200,
            {"minimum": minimum, "maximum": maximum},
        ),
        assumptions=(
            ModelAssumption("one_dimension", "Both cars move along one straight track."),
            ModelAssumption("instantaneous", "The collision happens instantaneously."),
            ModelAssumption("isolated", "No outside horizontal force changes total momentum."),
        ),
        completed=impact_time is not None,
        warnings=warnings,
        velocities_before=before,
        velocities_after=after,
        diagnostics=diagnostics,
        collision_time_s=impact_time,
        collided=impact_time is not None,
    )


@lru_cache(maxsize=128)
def collision_energy_scan(
    mass_a: float, mass_b: float, velocity_a: float, velocity_b: float, points: int = 25
):
    from physics_playground.performance import MAX_SCAN_POINTS, enforce_budget

    enforce_budget("Collision scan points", points, MAX_SCAN_POINTS)
    restitutions = tuple(index / (points - 1) for index in range(points))
    ratios = []
    for value in restitutions:
        result = simulate_collision(
            CollisionParameters(mass_a, mass_b, velocity_a, velocity_b, value)
        )
        before = result.diagnostics.kinetic_energy_before_j
        ratios.append(result.diagnostics.kinetic_energy_after_j / before if before else 0.0)
    return restitutions, tuple(ratios)
