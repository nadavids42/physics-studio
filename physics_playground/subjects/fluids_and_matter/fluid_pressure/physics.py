"""Pure hydrostatic gauge and absolute pressure model."""

import math
from dataclasses import dataclass

from physics_playground.validation import PhysicsValidationError


@dataclass(frozen=True, slots=True)
class FluidPressureParameters:
    fluid_density_kg_m3: float = 1000.0
    depth_m: float = 5.0
    gravity_m_s2: float = 9.81
    surface_pressure_pa: float = 101325.0
    maximum_depth_m: float = 10.0
    samples: int = 21

    def validate(self):
        values = (
            self.fluid_density_kg_m3,
            self.depth_m,
            self.gravity_m_s2,
            self.surface_pressure_pa,
            self.maximum_depth_m,
        )
        if not all(math.isfinite(v) for v in values):
            raise PhysicsValidationError("Pressure parameters must be finite.")
        if (
            self.fluid_density_kg_m3 <= 0
            or self.gravity_m_s2 <= 0
            or self.surface_pressure_pa < 0
            or self.maximum_depth_m <= 0
        ):
            raise PhysicsValidationError(
                "Density, gravity, and maximum depth must be positive; surface pressure cannot be negative."
            )
        if not 0 <= self.depth_m <= self.maximum_depth_m:
            raise PhysicsValidationError(
                "Selected depth must be between the surface and maximum depth."
            )
        if not 2 <= self.samples <= 201:
            raise PhysicsValidationError("Pressure samples must be between 2 and 201.")

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class PressureSample:
    depth_m: float
    gauge_pressure_pa: float
    absolute_pressure_pa: float


@dataclass(frozen=True, slots=True)
class FluidPressureResult:
    parameters: FluidPressureParameters
    gauge_pressure_pa: float
    absolute_pressure_pa: float
    pressure_increase_per_meter_pa: float
    samples: tuple[PressureSample, ...]
    outcome: str


def simulate(p: FluidPressureParameters) -> FluidPressureResult:
    p.validate()
    gradient = p.fluid_density_kg_m3 * p.gravity_m_s2
    gauge = gradient * p.depth_m
    absolute = p.surface_pressure_pa + gauge
    samples = tuple(
        PressureSample(
            d := p.maximum_depth_m * i / (p.samples - 1),
            gradient * d,
            p.surface_pressure_pa + gradient * d,
        )
        for i in range(p.samples)
    )
    return FluidPressureResult(
        p,
        gauge,
        absolute,
        gradient,
        samples,
        f"At {p.depth_m:.2f} m depth, gauge pressure is {gauge / 1000:.2f} kPa and absolute pressure is {absolute / 1000:.2f} kPa.",
    )
