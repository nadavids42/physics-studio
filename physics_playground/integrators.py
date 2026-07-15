"""Small, dependency-light numerical integration building blocks."""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

State = NDArray[np.float64]
Derivative = Callable[[State, float], State]


def euler_step(derivative: Derivative, state: State, time: float, dt: float) -> State:
    return state + dt * derivative(state, time)


def semi_implicit_euler_step(
    position: State,
    velocity: State,
    acceleration: Callable[[State], State],
    dt: float,
) -> tuple[State, State]:
    next_velocity = velocity + acceleration(position) * dt
    next_position = position + next_velocity * dt
    return next_position, next_velocity


def rk4_step(derivative: Derivative, state: State, time: float, dt: float) -> State:
    k1 = derivative(state, time)
    k2 = derivative(state + 0.5 * dt * k1, time + 0.5 * dt)
    k3 = derivative(state + 0.5 * dt * k2, time + 0.5 * dt)
    k4 = derivative(state + dt * k3, time + dt)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def velocity_verlet_step(
    position: State,
    velocity: State,
    acceleration: Callable[[State], State],
    dt: float,
) -> tuple[State, State]:
    current_acceleration = acceleration(position)
    next_position = position + velocity * dt + 0.5 * current_acceleration * dt**2
    next_acceleration = acceleration(next_position)
    next_velocity = velocity + 0.5 * (current_acceleration + next_acceleration) * dt
    return next_position, next_velocity
