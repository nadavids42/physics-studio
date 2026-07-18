"""Pure classical one-dimensional Doppler-effect model."""

import math
from dataclasses import dataclass
from enum import StrEnum

from physics_playground.units import ROOM_TEMPERATURE_SOUND_SPEED_M_S
from physics_playground.validation import PhysicsValidationError


class MotionOutcome(StrEnum):
    APPROACHING = "Approaching"
    RECEDING = "Receding"
    UNCHANGED = "Constant separation"


@dataclass(frozen=True, slots=True)
class DopplerParameters:
    source_frequency_hz: float = 440.0
    speed_of_sound_m_s: float = ROOM_TEMPERATURE_SOUND_SPEED_M_S
    source_velocity_m_s: float = 0.0
    observer_velocity_m_s: float = 0.0
    initial_source_position_m: float = 0.0
    initial_observer_position_m: float = 100.0
    duration_s: float = 2.0
    samples: int = 81

    def validate(self):
        values = tuple(float(getattr(self, k)) for k in self.__dataclass_fields__ if k != "samples")
        if not all(math.isfinite(x) for x in values):
            raise PhysicsValidationError("Doppler parameters must be finite.")
        if self.source_frequency_hz <= 0 or self.speed_of_sound_m_s <= 0 or self.duration_s <= 0:
            raise PhysicsValidationError(
                "Frequency, sound speed, and duration must be greater than zero."
            )
        if self.initial_observer_position_m <= self.initial_source_position_m:
            raise PhysicsValidationError(
                "In this one-dimensional model, place the observer to the right of the source."
            )
        if abs(self.source_velocity_m_s) >= self.speed_of_sound_m_s:
            raise PhysicsValidationError(
                "Source speed must remain below the speed of sound for the classical subsonic model."
            )
        if abs(self.observer_velocity_m_s) >= self.speed_of_sound_m_s:
            raise PhysicsValidationError("Observer speed must remain below the speed of sound.")
        if not 2 <= self.samples <= 241:
            raise PhysicsValidationError("Samples must be between 2 and 241.")

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class WavefrontFrame:
    time_s: float
    source_position_m: float
    observer_position_m: float
    centers_m: tuple[float, ...]
    radii_m: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class DopplerResult:
    parameters: DopplerParameters
    observed_frequency_hz: float
    frequency_shift_hz: float
    frequency_ratio: float
    motion: MotionOutcome
    wavelength_ahead_m: float
    wavelength_behind_m: float
    frames: tuple[WavefrontFrame, ...]
    outcome: str


def simulate(p: DopplerParameters) -> DopplerResult:
    p.validate()
    c = p.speed_of_sound_m_s
    observed = p.source_frequency_hz * (c - p.observer_velocity_m_s) / (c - p.source_velocity_m_s)
    relative = p.observer_velocity_m_s - p.source_velocity_m_s
    motion = (
        MotionOutcome.APPROACHING
        if relative < 0
        else (MotionOutcome.RECEDING if relative > 0 else MotionOutcome.UNCHANGED)
    )
    times = tuple(p.duration_s * i / (p.samples - 1) for i in range(p.samples))
    emission_step = max(1 / p.source_frequency_hz, p.duration_s / 24)
    emissions = []
    e = 0.0
    while e <= p.duration_s + 1e-12:
        emissions.append(e)
        e += emission_step
    frames = []
    for t in times:
        active = [et for et in emissions if et <= t]
        frames.append(
            WavefrontFrame(
                t,
                p.initial_source_position_m + p.source_velocity_m_s * t,
                p.initial_observer_position_m + p.observer_velocity_m_s * t,
                tuple(p.initial_source_position_m + p.source_velocity_m_s * et for et in active),
                tuple(c * (t - et) for et in active),
            )
        )
    shift = observed - p.source_frequency_hz
    direction = "higher" if shift > 1e-9 else ("lower" if shift < -1e-9 else "unchanged")
    return DopplerResult(
        p,
        observed,
        shift,
        observed / p.source_frequency_hz,
        motion,
        (c - p.source_velocity_m_s) / p.source_frequency_hz,
        (c + p.source_velocity_m_s) / p.source_frequency_hz,
        tuple(frames),
        f"The source and observer are {motion.value.lower()}, so the observed frequency is {observed:.1f} Hz ({direction} than {p.source_frequency_hz:.1f} Hz).",
    )
