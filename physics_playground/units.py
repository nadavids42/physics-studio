"""Units, physical constants, and consistent display formatting."""

from dataclasses import dataclass

EARTH_GRAVITY_M_S2 = 9.81
MOON_GRAVITY_M_S2 = 1.62
JUPITER_GRAVITY_M_S2 = 24.8
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
