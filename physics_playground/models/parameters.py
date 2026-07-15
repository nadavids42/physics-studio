"""Typed parameter models for every existing simulation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TunnelParameters:
    radius_m: float
    surface_gravity_m_s2: float
    start_fraction: float = 1.0


@dataclass(frozen=True, slots=True)
class PendulumParameters:
    length_m: float
    gravity_m_s2: float
    initial_angle_deg: float


@dataclass(frozen=True, slots=True)
class OrbitParameters:
    gravitational_parameter: float
    initial_radius: float
    tangential_speed: float
    time_step: float = 0.02


@dataclass(frozen=True, slots=True)
class ProjectileParameters:
    launch_speed_m_s: float
    launch_angle_deg: float
    gravity_m_s2: float
    initial_height_m: float = 0.0
    mass_kg: float | None = None
    drag_coefficient: float = 0.0


@dataclass(frozen=True, slots=True)
class SpringParameters:
    mass_kg: float
    stiffness_n_m: float
    initial_displacement_m: float
    damping_n_s_m: float = 0.0
    drive_amplitude_n: float = 0.0
    drive_angular_frequency_rad_s: float = 0.0


@dataclass(frozen=True, slots=True)
class DoublePendulumParameters:
    mass_1_kg: float
    mass_2_kg: float
    length_1_m: float
    length_2_m: float
    angle_1_deg: float
    angle_2_deg: float
    gravity_m_s2: float = 9.81


@dataclass(frozen=True, slots=True)
class CollisionParameters:
    mass_1_kg: float
    mass_2_kg: float
    velocity_1_m_s: float
    velocity_2_m_s: float
    restitution: float
