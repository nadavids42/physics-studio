"""Canonical physical constants, unit conversions, and display formatting.

Every constant name includes its SI unit. Values describe the simplified
reference environments used by Physics Studio, not locally measured values.
Simulation parameters remain configurable when the model allows them to vary.
"""

from dataclasses import dataclass

EARTH_GRAVITY_M_S2 = 9.81
MOON_GRAVITY_M_S2 = 1.62
JUPITER_GRAVITY_M_S2 = 24.8
MARS_GRAVITY_M_S2 = 3.71
EARTH_RADIUS_M = 6_371_000.0
MOON_RADIUS_M = 1_737_000.0
MARS_RADIUS_M = 3_390_000.0
STANDARD_ATMOSPHERE_PA = 101_325.0
ROOM_TEMPERATURE_SOUND_SPEED_M_S = 343.0
MOLAR_GAS_CONSTANT_J_MOL_K = 8.31446261815324
CELSIUS_ZERO_K = 273.15
METERS_PER_KILOMETER = 1_000.0
SECONDS_PER_MINUTE = 60.0


@dataclass(frozen=True, slots=True)
class GravityPreset:
    id: str
    label: str
    gravity_m_s2: float
    icon: str


GRAVITY_PRESETS = {
    "earth": GravityPreset("earth", "Earth", EARTH_GRAVITY_M_S2, "🌍"),
    "moon": GravityPreset("moon", "The Moon", MOON_GRAVITY_M_S2, "🌕"),
    "jupiter": GravityPreset("jupiter", "Jupiter", JUPITER_GRAVITY_M_S2, "🟠"),
}


@dataclass(frozen=True, slots=True)
class CelestialBodyPreset:
    id: str
    label: str
    radius_m: float
    surface_gravity_m_s2: float
    icon: str


CELESTIAL_BODY_PRESETS = {
    "earth": CelestialBodyPreset("earth", "Earth", EARTH_RADIUS_M, EARTH_GRAVITY_M_S2, "🌍"),
    "moon": CelestialBodyPreset("moon", "The Moon", MOON_RADIUS_M, MOON_GRAVITY_M_S2, "🌕"),
    "mars": CelestialBodyPreset("mars", "Mars", MARS_RADIUS_M, MARS_GRAVITY_M_S2, "🔴"),
}


def meters_to_kilometers(value: float) -> float:
    return value / METERS_PER_KILOMETER


def seconds_to_minutes(value: float) -> float:
    return value / SECONDS_PER_MINUTE


def format_measurement(value: float, unit: str, decimals: int = 1) -> str:
    return f"{value:.{decimals}f} {unit}"


def format_duration(seconds: float) -> str:
    if seconds < SECONDS_PER_MINUTE:
        return format_measurement(seconds, "s", 1)
    return format_measurement(seconds_to_minutes(seconds), "min", 1)
