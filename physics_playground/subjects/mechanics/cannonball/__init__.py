"""Cannonball vertical slice."""

from .physics import (
    ProjectileParameters,
    ProjectileResult,
    simulate_no_drag,
    simulate_quadratic_drag,
)

__all__ = (
    "ProjectileParameters",
    "ProjectileResult",
    "simulate_no_drag",
    "simulate_quadratic_drag",
)
