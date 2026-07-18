"""Streamlit-cached deterministic entry points for every pure simulation."""

import streamlit as st

from physics_playground.models.collision import CollisionParameters, simulate_collision
from physics_playground.models.double_pendulum import (
    DoublePendulumParameters,
    simulate_double_pendulum,
)
from physics_playground.models.earth_tunnel import TunnelParameters, simulate_tunnel
from physics_playground.performance import timed
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_no_drag,
    simulate_projectile,
)
from physics_playground.subjects.mechanics.orbital_gravity.physics import (
    OrbitParameters,
    simulate_orbit,
)
from physics_playground.subjects.waves_and_oscillations.boing.physics import (
    SpringParameters,
    simulate_spring,
)
from physics_playground.subjects.waves_and_oscillations.pendulum.physics import (
    PendulumParameters,
    simulate_pendulum,
)


def cached(name):
    """Decorate a simulation function with timing inside Streamlit's cache.

    The extra decorator level is essential: ``timed(name)`` returns a
    decorator, not a simulation function. Caching that decorator would make
    Streamlit try to hash the wrapped function during module import.
    """

    def decorator(function):
        timed_function = timed(name)(function)
        return st.cache_data(show_spinner=False, max_entries=128, ttl=3600)(timed_function)

    return decorator


@cached("collision")
def cached_collision(p: CollisionParameters):
    return simulate_collision(p)


@cached("projectile_no_drag")
def cached_projectile_no_drag(p: ProjectileParameters):
    return simulate_no_drag(p)


@cached("projectile")
def cached_projectile(p: ProjectileParameters):
    return simulate_projectile(p)


@cached("spring")
def cached_spring(p: SpringParameters):
    return simulate_spring(p)


@cached("pendulum")
def cached_pendulum(p: PendulumParameters):
    return simulate_pendulum(p)


@cached("orbit")
def cached_orbit(p: OrbitParameters):
    return simulate_orbit(p)


@cached("tunnel")
def cached_tunnel(p: TunnelParameters):
    return simulate_tunnel(p)


@cached("double_pendulum")
def cached_double_pendulum(p: DoublePendulumParameters):
    return simulate_double_pendulum(p)
