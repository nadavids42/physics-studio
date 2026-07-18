"""Pure Archimedes-principle buoyancy model."""

import math
from dataclasses import dataclass
from enum import StrEnum

from physics_playground.validation import PhysicsValidationError


class BuoyancyInputMode(StrEnum):
    DENSITY = "Set object density"
    MASS = "Set object mass"


class BuoyancyState(StrEnum):
    FLOATING = "Floating"
    SINKING = "Sinking"
    NEUTRAL = "Neutral buoyancy"


@dataclass(frozen=True, slots=True)
class BuoyancyParameters:
    input_mode: BuoyancyInputMode = BuoyancyInputMode.DENSITY
    object_density_kg_m3: float = 600.0
    object_mass_kg: float = 6.0
    object_volume_m3: float = 0.01
    fluid_density_kg_m3: float = 1000.0
    gravity_m_s2: float = 9.81

    def validate(self):
        try:
            BuoyancyInputMode(self.input_mode)
        except ValueError as exc:
            raise PhysicsValidationError(
                "Choose density-based or mass-based object input."
            ) from exc
        values = (
            self.object_density_kg_m3,
            self.object_mass_kg,
            self.object_volume_m3,
            self.fluid_density_kg_m3,
            self.gravity_m_s2,
        )
        if not all(math.isfinite(v) for v in values):
            raise PhysicsValidationError("Buoyancy parameters must be finite.")
        if min(values) <= 0:
            raise PhysicsValidationError(
                "Density, mass, volume, fluid density, and gravity must be greater than zero."
            )

    def to_dict(self):
        return {
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "input_mode": BuoyancyInputMode(self.input_mode).value,
        }


@dataclass(frozen=True, slots=True)
class BuoyancyResult:
    parameters: BuoyancyParameters
    state: BuoyancyState
    effective_density_kg_m3: float
    effective_mass_kg: float
    submerged_fraction: float
    displaced_volume_m3: float
    weight_n: float
    buoyant_force_n: float
    maximum_buoyant_force_n: float
    apparent_weight_n: float
    net_vertical_force_n: float
    outcome: str


def simulate(p: BuoyancyParameters) -> BuoyancyResult:
    p.validate()
    mode = BuoyancyInputMode(p.input_mode)
    density = (
        p.object_density_kg_m3
        if mode is BuoyancyInputMode.DENSITY
        else p.object_mass_kg / p.object_volume_m3
    )
    mass = density * p.object_volume_m3 if mode is BuoyancyInputMode.DENSITY else p.object_mass_kg
    ratio = density / p.fluid_density_kg_m3
    tolerance = 1e-9
    if abs(ratio - 1) <= tolerance:
        state = BuoyancyState.NEUTRAL
        fraction = 1.0
    elif ratio < 1:
        state = BuoyancyState.FLOATING
        fraction = ratio
    else:
        state = BuoyancyState.SINKING
        fraction = 1.0
    displaced = p.object_volume_m3 * fraction
    weight = mass * p.gravity_m_s2
    maximum = p.fluid_density_kg_m3 * p.object_volume_m3 * p.gravity_m_s2
    buoyant = p.fluid_density_kg_m3 * displaced * p.gravity_m_s2
    net = buoyant - weight
    apparent = max(0.0, weight - buoyant)
    return BuoyancyResult(
        p,
        state,
        density,
        mass,
        fraction,
        displaced,
        weight,
        buoyant,
        maximum,
        apparent,
        net,
        f"The object is {state.value.lower()}: {fraction:.1%} is submerged, buoyant force is {buoyant:.2f} N, and apparent weight is {apparent:.2f} N.",
    )
