"""Pure one-dimensional traveling-wave superposition model."""

import math
from dataclasses import dataclass

from physics_playground.validation import PhysicsValidationError


@dataclass(frozen=True, slots=True)
class WaveSource:
    amplitude: float = 1.0
    wavelength_m: float = 2.0
    frequency_hz: float = 1.0
    phase_rad: float = 0.0

    @property
    def propagation_speed_m_s(self):
        return self.wavelength_m * self.frequency_hz

    def validate(self):
        values = (self.amplitude, self.wavelength_m, self.frequency_hz, self.phase_rad)
        if not all(math.isfinite(x) for x in values):
            raise PhysicsValidationError("Wave source values must be finite.")
        if self.amplitude < 0:
            raise PhysicsValidationError("Amplitude cannot be negative.")
        if self.wavelength_m <= 0 or self.frequency_hz <= 0:
            raise PhysicsValidationError("Wavelength and frequency must be greater than zero.")

    def to_dict(self):
        return {
            "amplitude": self.amplitude,
            "wavelength_m": self.wavelength_m,
            "frequency_hz": self.frequency_hz,
            "phase_rad": self.phase_rad,
            "propagation_speed_m_s": self.propagation_speed_m_s,
        }


@dataclass(frozen=True, slots=True)
class WaveInterferenceParameters:
    sources: tuple[WaveSource, ...] = (WaveSource(), WaveSource(1, 2, 1, 0))
    domain_length_m: float = 10.0
    duration_s: float = 2.0
    position_samples: int = 161
    time_samples: int = 81

    def validate(self):
        if len(self.sources) < 2 or len(self.sources) > 6:
            raise PhysicsValidationError("Use between two and six wave sources.")
        for source in self.sources:
            source.validate()
        if (
            not math.isfinite(self.domain_length_m)
            or not math.isfinite(self.duration_s)
            or self.domain_length_m <= 0
            or self.duration_s <= 0
        ):
            raise PhysicsValidationError(
                "Domain length and duration must be finite and greater than zero."
            )
        if not 21 <= self.position_samples <= 501 or not 2 <= self.time_samples <= 241:
            raise PhysicsValidationError("Position samples must be 21–501 and time samples 2–241.")

    def to_dict(self):
        return {
            "sources": [s.to_dict() for s in self.sources],
            "domain_length_m": self.domain_length_m,
            "duration_s": self.duration_s,
            "position_samples": self.position_samples,
            "time_samples": self.time_samples,
        }


@dataclass(frozen=True, slots=True)
class WaveMeasurement:
    position_m: float
    minimum_displacement: float
    maximum_displacement: float
    rms_displacement: float


@dataclass(frozen=True, slots=True)
class WaveInterferenceResult:
    parameters: WaveInterferenceParameters
    position_m: tuple[float, ...]
    time_s: tuple[float, ...]
    source_frames: tuple[tuple[tuple[float, ...], ...], ...]
    superposition_frames: tuple[tuple[float, ...], ...]
    measurements: tuple[WaveMeasurement, ...]
    maximum_amplitude: float
    minimum_amplitude: float
    outcome: str

    def displacement_at(self, position_m: float, time_s: float) -> float:
        return sum(
            s.amplitude
            * math.sin(
                2 * math.pi * (position_m / s.wavelength_m - s.frequency_hz * time_s) + s.phase_rad
            )
            for s in self.parameters.sources
        )


def _measurement(result_positions, frames, index):
    values = [frame[index] for frame in frames]
    rms = math.sqrt(sum(x * x for x in values) / len(values))
    return WaveMeasurement(result_positions[index], min(values), max(values), rms)


def simulate(p: WaveInterferenceParameters) -> WaveInterferenceResult:
    p.validate()
    x = tuple(p.domain_length_m * i / (p.position_samples - 1) for i in range(p.position_samples))
    t = tuple(p.duration_s * i / (p.time_samples - 1) for i in range(p.time_samples))
    per_source = []
    for s in p.sources:
        per_source.append(
            tuple(
                tuple(
                    s.amplitude
                    * math.sin(
                        2 * math.pi * (position / s.wavelength_m - s.frequency_hz * time)
                        + s.phase_rad
                    )
                    for position in x
                )
                for time in t
            )
        )
    total = tuple(
        tuple(
            sum(per_source[source][ti][xi] for source in range(len(p.sources)))
            for xi in range(len(x))
        )
        for ti in range(len(t))
    )
    indices = (0, len(x) // 4, len(x) // 2, 3 * len(x) // 4, len(x) - 1)
    measurements = tuple(_measurement(x, total, i) for i in indices)
    maximum = max(max(frame) for frame in total)
    minimum = min(min(frame) for frame in total)
    ratio = max(abs(maximum), abs(minimum)) / max(1e-12, sum(s.amplitude for s in p.sources))
    kind = (
        "strong constructive interference"
        if ratio > 0.9
        else (
            "substantial cancellation"
            if ratio < 0.25
            else "alternating constructive and destructive interference"
        )
    )
    return WaveInterferenceResult(
        p,
        x,
        t,
        tuple(per_source),
        total,
        measurements,
        maximum,
        minimum,
        f"The waves show {kind}; the largest displacement is {max(abs(maximum), abs(minimum)):.2f}.",
    )
