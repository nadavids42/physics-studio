"""Pure paired double-pendulum chaos model."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

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
from physics_playground.integrators import rk4_step
from physics_playground.performance import (
    MAX_INTEGRATION_STEPS,
    enforce_budget,
    recommended_time_step,
    stability_message,
    validate_finite_parameters,
)
from physics_playground.serialization import to_jsonable
from physics_playground.units import EARTH_GRAVITY_M_S2
from physics_playground.validation import PhysicsValidationError, require_positive


@dataclass(frozen=True, slots=True)
class DoublePendulumParameters:
    mass_1_kg: float = 1.0
    mass_2_kg: float = 1.0
    length_1_m: float = 1.5
    length_2_m: float = 1.5
    angle_1_deg: float = 110.0
    angle_2_deg: float = -20.0
    perturbation_deg: float = 0.1
    gravity_m_s2: float = EARTH_GRAVITY_M_S2
    duration_s: float = 15.0
    time_step_s: float = 0.005

    def validate(self):
        validate_finite_parameters(self)
        for n, v in (
            ("Mass 1", self.mass_1_kg),
            ("Mass 2", self.mass_2_kg),
            ("Length 1", self.length_1_m),
            ("Length 2", self.length_2_m),
            ("Gravity", self.gravity_m_s2),
            ("Duration", self.duration_s),
            ("Time step", self.time_step_s),
        ):
            require_positive(n, v)
        if self.perturbation_deg < 0:
            raise PhysicsValidationError("Perturbation cannot be negative.")
        enforce_budget(
            "Double-pendulum integration steps",
            math.ceil(self.duration_s / self.time_step_s),
            MAX_INTEGRATION_STEPS,
        )

    def to_dict(self):
        return to_jsonable(asdict(self))


@dataclass(frozen=True, slots=True)
class DoublePendulumResult(ContractResult[DoublePendulumParameters]):
    initial_angular_separation_rad: float = 0.0
    final_angular_separation_rad: float = 0.0
    final_cartesian_separation_m: float = 0.0
    divergence_rate_per_s: float | None = None
    energy_drift_fraction: float = 0.0


def convergence_warning(p):
    scale = math.sqrt(min(p.length_1_m, p.length_2_m) / p.gravity_m_s2)
    return stability_message(
        p.time_step_s, recommended_time_step(scale, 0.02), "double-pendulum time step"
    )


def derivative(s, p):
    t1, w1, t2, w2 = s
    m1, m2, L1, L2, g = p.mass_1_kg, p.mass_2_kg, p.length_1_m, p.length_2_m, p.gravity_m_s2
    d = t1 - t2
    den1 = L1 * (2 * m1 + m2 - m2 * math.cos(2 * d))
    den2 = L2 * (2 * m1 + m2 - m2 * math.cos(2 * d))
    a1 = (
        -g * (2 * m1 + m2) * math.sin(t1)
        - m2 * g * math.sin(t1 - 2 * t2)
        - 2 * math.sin(d) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * math.cos(d))
    ) / den1
    a2 = (
        2
        * math.sin(d)
        * (
            w1 * w1 * L1 * (m1 + m2)
            + g * (m1 + m2) * math.cos(t1)
            + w2 * w2 * L2 * m2 * math.cos(d)
        )
    ) / den2
    return np.array((w1, a1, w2, a2))


def integrate(p, perturbation_deg=0.0):
    count = int(round(p.duration_s / p.time_step_s)) + 1
    t = np.linspace(0, p.duration_s, count)
    dt = t[1] - t[0]
    s = np.zeros((count, 4))
    s[0] = (math.radians(p.angle_1_deg + perturbation_deg), 0, math.radians(p.angle_2_deg), 0)
    for i in range(1, count):
        s[i] = rk4_step(lambda state, _time: derivative(state, p), s[i - 1], t[i - 1], dt)
    return t, s


def cartesian(states, p):
    t1 = states[:, 0]
    t2 = states[:, 2]
    x1 = p.length_1_m * np.sin(t1)
    y1 = -p.length_1_m * np.cos(t1)
    x2 = x1 + p.length_2_m * np.sin(t2)
    y2 = y1 - p.length_2_m * np.cos(t2)
    return x1, y1, x2, y2


def total_energy(states, p):
    t1, w1, t2, w2 = states.T
    m1, m2, L1, L2, g = p.mass_1_kg, p.mass_2_kg, p.length_1_m, p.length_2_m, p.gravity_m_s2
    kinetic = (
        0.5 * (m1 + m2) * L1**2 * w1**2
        + 0.5 * m2 * L2**2 * w2**2
        + m2 * L1 * L2 * w1 * w2 * np.cos(t1 - t2)
    )
    potential = -(m1 + m2) * g * L1 * np.cos(t1) - m2 * g * L2 * np.cos(t2)
    return kinetic + potential


def simulate_double_pendulum(p):
    p.validate()
    t, a = integrate(p, 0)
    _, b = integrate(p, p.perturbation_deg)
    a1y, a1v, a2x, a2y = cartesian(a, p)
    b1x, b1y, b2x, b2y = cartesian(b, p)
    angular = np.sqrt((a[:, 0] - b[:, 0]) ** 2 + (a[:, 2] - b[:, 2]) ** 2)
    cart = np.hypot(a2x - b2x, a2y - b2y)
    logsep = np.log(np.maximum(cart, 1e-12))
    energy = total_energy(a, p)
    drift = float(np.max(np.abs(energy - energy[0])) / max(abs(float(energy[0])), 1e-12))
    mask = (cart > max(cart[0] * 2, 1e-8)) & (cart < (p.length_1_m + p.length_2_m) * 0.5)
    rate = float(np.polyfit(t[mask], logsep[mask], 1)[0]) if np.count_nonzero(mask) >= 8 else None
    warning = convergence_warning(p)
    warnings = (warning,) if warning else ()
    plots = (
        PlotData(
            "energy",
            "Total energy",
            "Time (s)",
            "Energy (J)",
            (PlotSeries("energy", "E(t)", tuple(t), tuple(energy)),),
        ),
        PlotData(
            "angular_separation",
            "Angular separation",
            "Time (s)",
            "Separation (rad)",
            (PlotSeries("angular", "Δθ", tuple(t), tuple(angular)),),
        ),
        PlotData(
            "cartesian_separation",
            "Cartesian separation",
            "Time (s)",
            "Separation (m)",
            (PlotSeries("cartesian", "Δr", tuple(t), tuple(cart)),),
        ),
        PlotData(
            "log_separation",
            "Log separation",
            "Time (s)",
            "ln separation",
            (PlotSeries("log", "ln Δr", tuple(t), tuple(logsep)),),
        ),
        PlotData(
            "phase_1",
            "Arm 1 phase space",
            "θ₁ (rad)",
            "ω₁ (rad/s)",
            (PlotSeries("phase1", "Arm 1", tuple(a[:, 0]), tuple(a[:, 1])),),
            PlotKind.PHASE,
        ),
        PlotData(
            "phase_2",
            "Arm 2 phase space",
            "θ₂ (rad)",
            "ω₂ (rad/s)",
            (PlotSeries("phase2", "Arm 2", tuple(a[:, 2]), tuple(a[:, 3])),),
            PlotKind.PHASE,
        ),
    )
    tracks = (
        AnimationTrack("a_joint", "System A joint", tuple(a1y), tuple(a1v), {"color": "#42A5F5"}),
        AnimationTrack("a_bob", "System A bob", tuple(a2x), tuple(a2y), {"color": "#1565C0"}),
        AnimationTrack("b_joint", "System B joint", tuple(b1x), tuple(b1y), {"color": "#FFB74D"}),
        AnimationTrack("b_bob", "System B bob", tuple(b2x), tuple(b2y), {"color": "#E65100"}),
    )
    return DoublePendulumResult(
        simulation_id="double_pendulum",
        parameters=p,
        metrics=(
            SummaryMetric("energy_drift", "Energy drift", drift * 100, "%", f"{drift * 100:.4f}%"),
            SummaryMetric(
                "angular_separation",
                "Final angular separation",
                float(angular[-1]),
                "rad",
                f"{angular[-1]:.3f} rad",
            ),
            SummaryMetric(
                "cartesian_separation",
                "Final Cartesian separation",
                float(cart[-1]),
                "m",
                f"{cart[-1]:.3f} m",
            ),
            SummaryMetric(
                "divergence_rate",
                "Approximate divergence rate",
                rate or 0,
                "1/s",
                f"{rate:.3f} 1/s" if rate is not None else "n/a",
            ),
        ),
        events=(
            SimulationEvent("release", EventKind.START, 0, "Both pendulums released"),
            SimulationEvent(
                "complete", EventKind.COMPLETION, p.duration_s, "Chaos comparison complete"
            ),
        ),
        plots=plots,
        animation=AnimationData(
            AnimationKind.TWO_DIMENSIONAL,
            tuple(t),
            tracks,
            6000,
            {"minimum": -(p.length_1_m + p.length_2_m), "maximum": p.length_1_m + p.length_2_m},
        ),
        assumptions=(
            ModelAssumption("point_masses", "Both bobs are point masses."),
            ModelAssumption("rigid_rods", "Rods are massless and rigid."),
            ModelAssumption("no_damping", "No drag or pivot friction removes energy."),
        ),
        warnings=warnings,
        initial_angular_separation_rad=float(angular[0]),
        final_angular_separation_rad=float(angular[-1]),
        final_cartesian_separation_m=float(cart[-1]),
        divergence_rate_per_s=rate,
        energy_drift_fraction=drift,
    )
