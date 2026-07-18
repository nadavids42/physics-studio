"""Pure calculations reused by multiple mechanics simulations."""

import math

from physics_playground.validation import PhysicsValidationError


def require_finite(**values: float) -> None:
    if not all(math.isfinite(value) for value in values.values()):
        raise PhysicsValidationError("Every parameter must be a finite number.")


def weight(mass_kg: float, gravity_m_s2: float) -> float:
    return mass_kg * gravity_m_s2


def moment(force_n: float, lever_arm_m: float) -> float:
    return force_n * lever_arm_m


def weighted_position(masses_kg: tuple[float, ...], positions_m: tuple[float, ...]) -> float:
    total = sum(masses_kg)
    if total <= 0:
        raise PhysicsValidationError("Total mass must be greater than zero.")
    return sum(m * x for m, x in zip(masses_kg, positions_m, strict=True)) / total
