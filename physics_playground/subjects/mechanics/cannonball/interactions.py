"""Pure Cannonball interaction policies used by its Streamlit page."""

from __future__ import annotations

import random
from collections.abc import Callable

from physics_playground.presentation.learning_modes import ChangedVariable
from physics_playground.units import EARTH_GRAVITY_M_S2, MOON_GRAVITY_M_S2

from .physics import ProjectileParameters, ProjectileResult

ProjectileRunner = Callable[[ProjectileParameters], ProjectileResult]


def target_for_seed(seed: int) -> float:
    return round(random.Random(seed).uniform(15, 55), 1)


def target_message(result: ProjectileResult, target_m: float) -> str:
    if not result.landed:
        return "The simulation limit was reached before the cannonball landed."
    miss = result.range_m - target_m
    return (
        f"🎯 BULLSEYE! Landed at {result.range_m:.1f} m."
        if abs(miss) <= 2
        else f"Missed by {abs(miss):.1f} m ({'long' if miss > 0 else 'short'})."
    )


def notebook_metrics(result: ProjectileResult) -> dict[str, float]:
    return {
        "range_m": result.range_m,
        "maximum_height_m": result.maximum_height_m,
        "flight_time_s": result.flight_time_s,
        "impact_speed_m_s": result.impact_speed_m_s or 0.0,
        "energy_lost_j": result.metric("energy_lost").value,
    }


def comparison_results(
    kind: str, run: ProjectileRunner
) -> tuple[ProjectileResult, ProjectileResult, tuple[str, str], ChangedVariable]:
    if kind == "30° versus 60°":
        first = run(ProjectileParameters(25, 30, EARTH_GRAVITY_M_S2))
        second = run(ProjectileParameters(25, 60, EARTH_GRAVITY_M_S2))
        return first, second, ("30°", "60°"), ChangedVariable("Launch angle", "30°", "60°")
    if kind == "With drag versus without drag":
        first = run(ProjectileParameters(25, 40, EARTH_GRAVITY_M_S2))
        second = run(ProjectileParameters(25, 40, EARTH_GRAVITY_M_S2, drag_coefficient_kg_m=0.05))
        return (
            first,
            second,
            ("No drag", "Quadratic drag"),
            ChangedVariable("Air resistance", "None", "Quadratic drag"),
        )
    first = run(ProjectileParameters(25, 45, EARTH_GRAVITY_M_S2))
    second = run(ProjectileParameters(25, 45, MOON_GRAVITY_M_S2))
    return (
        first,
        second,
        ("Earth", "Moon"),
        ChangedVariable("Gravity", f"{EARTH_GRAVITY_M_S2} m/s²", f"{MOON_GRAVITY_M_S2} m/s²"),
    )
