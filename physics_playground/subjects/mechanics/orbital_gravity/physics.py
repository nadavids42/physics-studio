"""Pure two-body orbital physics with velocity-Verlet integration."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import StrEnum

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
    MAX_INTEGRATION_STEPS,
    enforce_budget,
    recommended_time_step,
    stability_message,
    validate_finite_parameters,
)
from physics_playground.serialization import to_jsonable
from physics_playground.validation import PhysicsValidationError, require_positive


class OrbitOutcome(StrEnum):
    CRASH = "Crash"
    ELLIPTICAL = "Bound elliptical orbit"
    CIRCULAR = "Approximately circular orbit"
    ESCAPE = "Escape"


@dataclass(frozen=True, slots=True)
class OrbitParameters:
    gravitational_parameter: float = 20.0
    launch_radius: float = 7.0
    tangential_speed: float = 1.69
    time_step: float = 0.02
    steps: int = 5000
    collision_radius: float = 0.35
    escape_radius: float = 80.0

    def validate(self):
        validate_finite_parameters(self)
        require_positive("Central gravity μ", self.gravitational_parameter)
        require_positive("Launch radius", self.launch_radius)
        require_positive("Time step", self.time_step)
        require_positive("Collision radius", self.collision_radius)
        require_positive("Escape radius", self.escape_radius)
        if self.launch_radius <= self.collision_radius:
            raise PhysicsValidationError("Launch radius must be outside the central body.")
        if self.steps < 2:
            raise PhysicsValidationError("Steps must be at least 2.")
        enforce_budget("Orbital integration steps", self.steps, MAX_INTEGRATION_STEPS)

    @property
    def circular_speed(self):
        return math.sqrt(self.gravitational_parameter / self.launch_radius)

    @property
    def escape_speed(self):
        return math.sqrt(2 * self.gravitational_parameter / self.launch_radius)

    @property
    def circular_period(self):
        return 2 * math.pi * math.sqrt(self.launch_radius**3 / self.gravitational_parameter)

    def to_dict(self):
        return to_jsonable(asdict(self))


@dataclass(frozen=True, slots=True)
class OrbitResult(ContractResult[OrbitParameters]):
    outcome: OrbitOutcome = OrbitOutcome.ELLIPTICAL
    eccentricity: float = 0.0
    periapsis: float | None = None
    apoapsis: float | None = None
    energy_drift_fraction: float = 0.0
    angular_momentum_drift_fraction: float = 0.0


def _acceleration(r, mu):
    d = np.linalg.norm(r)
    return -mu * r / d**3


def _invariants(r, v, mu):
    radius = np.linalg.norm(r, axis=1)
    speed2 = np.sum(v * v, axis=1)
    ke = 0.5 * speed2
    pe = -mu / radius
    energy = ke + pe
    h = r[:, 0] * v[:, 1] - r[:, 1] * v[:, 0]
    return radius, ke, pe, energy, h


def _classify(mu, r0, v0, crashed, escaped):
    if crashed:
        return OrbitOutcome.CRASH
    energy = 0.5 * v0 * v0 - mu / r0
    e = abs(1 - r0 * v0 * v0 / mu)
    if escaped or energy >= 0:
        return OrbitOutcome.ESCAPE
    return OrbitOutcome.CIRCULAR if e < 0.03 else OrbitOutcome.ELLIPTICAL


def _elements(mu, r0, v0):
    energy = 0.5 * v0 * v0 - mu / r0
    e = abs(1 - r0 * v0 * v0 / mu)
    if energy >= 0:
        return e, None, None
    a = -mu / (2 * energy)
    return e, a * (1 - e), a * (1 + e)


def timestep_warning(p):
    return stability_message(
        p.time_step, recommended_time_step(p.circular_period, 0.02), "orbital time step"
    )


def _build(p, t, r, v, method, crashed=False, escaped=False):
    radius, ke, pe, total, h = _invariants(r, v, p.gravitational_parameter)
    e, peri, apo = _elements(p.gravitational_parameter, p.launch_radius, p.tangential_speed)
    ed = float(np.max(np.abs(total - total[0])) / max(abs(total[0]), 1e-12))
    hd = float(np.max(np.abs(h - h[0])) / max(abs(h[0]), 1e-12))
    outcome = _classify(
        p.gravitational_parameter, p.launch_radius, p.tangential_speed, crashed, escaped
    )
    warning = timestep_warning(p)
    warnings = (warning,) if warning else ()
    events = [SimulationEvent("launch", EventKind.START, 0, "Planet launched")]
    if crashed:
        events.append(
            SimulationEvent(
                "crash", EventKind.COLLISION, float(t[-1]), "Planet hit the central body"
            )
        )
    elif escaped:
        events.append(
            SimulationEvent(
                "escape", EventKind.COMPLETION, float(t[-1]), "Planet crossed the escape boundary"
            )
        )
    else:
        events.append(
            SimulationEvent("complete", EventKind.COMPLETION, float(t[-1]), outcome.value)
        )
    plots = (
        PlotData(
            "energy",
            "Orbital energy",
            "Time",
            "Specific energy",
            (
                PlotSeries("kinetic", "Kinetic", tuple(t), tuple(ke)),
                PlotSeries("potential", "Potential", tuple(t), tuple(pe)),
                PlotSeries("total", "Total", tuple(t), tuple(total)),
            ),
        ),
        PlotData(
            "angular_momentum",
            "Angular momentum",
            "Time",
            "Specific angular momentum",
            (PlotSeries("h", "h", tuple(t), tuple(h)),),
        ),
        PlotData(
            "radius",
            "Distance from central body",
            "Time",
            "Radius",
            (PlotSeries("radius", "r", tuple(t), tuple(radius)),),
        ),
    )
    view = max(float(np.max(np.abs(r))), p.launch_radius) * 1.15
    return OrbitResult(
        simulation_id="orbital_gravity",
        parameters=p,
        metrics=(
            SummaryMetric("eccentricity", "Eccentricity", e, "", f"{e:.4f}"),
            SummaryMetric(
                "periapsis", "Periapsis", peri or 0, "", f"{peri:.2f}" if peri else "n/a"
            ),
            SummaryMetric("apoapsis", "Apoapsis", apo or 0, "", f"{apo:.2f}" if apo else "n/a"),
            SummaryMetric("energy_drift", "Energy drift", ed * 100, "%", f"{ed * 100:.4f}%"),
            SummaryMetric(
                "angular_momentum_drift",
                "Angular momentum drift",
                hd * 100,
                "%",
                f"{hd * 100:.4f}%",
            ),
        ),
        events=tuple(events),
        plots=plots,
        animation=AnimationData(
            AnimationKind.TWO_DIMENSIONAL,
            tuple(t),
            (
                AnimationTrack(
                    "planet", "Planet", tuple(r[:, 0]), tuple(r[:, 1]), {"color": "#42A5F5"}
                ),
            ),
            5000,
            {"minimum": -view, "maximum": view},
        ),
        assumptions=(
            ModelAssumption("fixed_center", "The central mass stays fixed."),
            ModelAssumption("test_particle", "The planet does not affect the central body."),
            ModelAssumption("no_perturbations", "No other bodies or drag perturb the orbit."),
        ),
        warnings=warnings,
        outcome=outcome,
        eccentricity=e,
        periapsis=peri,
        apoapsis=apo,
        energy_drift_fraction=ed,
        angular_momentum_drift_fraction=hd,
    )


def simulate_orbit(p: OrbitParameters) -> OrbitResult:
    p.validate()
    r = np.zeros((p.steps, 2))
    v = np.zeros((p.steps, 2))
    t = np.arange(p.steps) * p.time_step
    r[0] = (p.launch_radius, 0)
    v[0] = (0, p.tangential_speed)
    last = p.steps - 1
    crashed = escaped = False
    a = _acceleration(r[0], p.gravitational_parameter)
    for i in range(1, p.steps):
        rn = r[i - 1] + v[i - 1] * p.time_step + 0.5 * a * p.time_step**2
        an = _acceleration(rn, p.gravitational_parameter)
        vn = v[i - 1] + 0.5 * (a + an) * p.time_step
        r[i] = rn
        v[i] = vn
        a = an
        d = np.linalg.norm(rn)
        if d <= p.collision_radius:
            crashed = True
            last = i
            break
        if d >= p.escape_radius and np.dot(rn, vn) > 0:
            escaped = True
            last = i
            break
    return _build(
        p, t[: last + 1], r[: last + 1], v[: last + 1], "Velocity Verlet", crashed, escaped
    )


def simulate_orbit_legacy_euler(p: OrbitParameters) -> OrbitResult:
    """Previous semi-implicit Euler method retained only for regression comparison."""
    p.validate()
    r = np.zeros((p.steps, 2))
    v = np.zeros((p.steps, 2))
    t = np.arange(p.steps) * p.time_step
    r[0] = (p.launch_radius, 0)
    v[0] = (0, p.tangential_speed)
    for i in range(1, p.steps):
        v[i] = v[i - 1] + _acceleration(r[i - 1], p.gravitational_parameter) * p.time_step
        r[i] = r[i - 1] + v[i] * p.time_step
    return _build(p, t, r, v, "Semi-implicit Euler")
