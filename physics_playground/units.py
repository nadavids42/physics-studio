"""Canonical physical constants, unit conversions, and display formatting.

Every constant name includes its SI unit. Values describe the simplified
reference environments used by Physics Studio, not locally measured values.
Simulation parameters remain configurable when the model allows them to vary.
"""

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
