"""Pure ideal-gas and named gas-law state comparisons."""

import math
from dataclasses import dataclass
from enum import StrEnum

from physics_playground.validation import PhysicsValidationError

GAS_CONSTANT_J_MOL_K = 8.31446261815324


class GasLawScenario(StrEnum):
    IDEAL = "Ideal gas state"
    BOYLE = "Boyle's law"
    CHARLES = "Charles's law"
    GAY_LUSSAC = "Gay-Lussac's law"


def celsius_to_kelvin(celsius: float) -> float:
    if not math.isfinite(celsius):
        raise PhysicsValidationError("Temperature must be finite.")
    kelvin = celsius + 273.15
    if kelvin <= 0:
        raise PhysicsValidationError("Temperature must be above absolute zero (−273.15 °C).")
    return kelvin


@dataclass(frozen=True, slots=True)
class GasLawParameters:
    scenario: GasLawScenario = GasLawScenario.IDEAL
    amount_mol: float = 1.0
    pressure_pa: float = 101325.0
    volume_m3: float = 0.024
    temperature_k: float = 293.15
    target_volume_m3: float = 0.012
    target_temperature_k: float = 373.15

    def validate(self):
        try:
            GasLawScenario(self.scenario)
        except ValueError as exc:
            raise PhysicsValidationError("Choose a supported gas-law scenario.") from exc
        values = (
            self.amount_mol,
            self.pressure_pa,
            self.volume_m3,
            self.temperature_k,
            self.target_volume_m3,
            self.target_temperature_k,
        )
        if not all(math.isfinite(v) for v in values):
            raise PhysicsValidationError("Gas-law parameters must be finite.")
        if (
            self.amount_mol <= 0
            or self.pressure_pa <= 0
            or self.volume_m3 <= 0
            or self.target_volume_m3 <= 0
        ):
            raise PhysicsValidationError("Amount, pressure, and volumes must be greater than zero.")
        if self.temperature_k <= 0 or self.target_temperature_k <= 0:
            raise PhysicsValidationError("Absolute temperatures must be greater than zero kelvin.")

    def to_dict(self):
        return {
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "scenario": GasLawScenario(self.scenario).value,
        }


@dataclass(frozen=True, slots=True)
class GasState:
    pressure_pa: float
    volume_m3: float
    temperature_k: float
    amount_mol: float

    @property
    def ideal_residual_j(self):
        return (
            self.pressure_pa * self.volume_m3
            - self.amount_mol * GAS_CONSTANT_J_MOL_K * self.temperature_k
        )


@dataclass(frozen=True, slots=True)
class GasLawResult:
    parameters: GasLawParameters
    scenario: GasLawScenario
    state_a: GasState
    state_b: GasState
    constant_variables: tuple[str, ...]
    changed_variable: str
    invariant_name: str
    invariant_a: float
    invariant_b: float
    outcome: str


def simulate(p: GasLawParameters) -> GasLawResult:
    p.validate()
    scenario = GasLawScenario(p.scenario)
    n = p.amount_mol
    R = GAS_CONSTANT_J_MOL_K
    if scenario is GasLawScenario.IDEAL:
        pressure = n * R * p.temperature_k / p.volume_m3
        a = GasState(pressure, p.volume_m3, p.temperature_k, n)
        b = a
        constants = ("amount",)
        changed = "none"
        name = "PV/(nT)"
        ia = ib = pressure * p.volume_m3 / (n * p.temperature_k)
    elif scenario is GasLawScenario.BOYLE:
        p1 = n * R * p.temperature_k / p.volume_m3
        p2 = n * R * p.temperature_k / p.target_volume_m3
        a = GasState(p1, p.volume_m3, p.temperature_k, n)
        b = GasState(p2, p.target_volume_m3, p.temperature_k, n)
        constants = ("temperature", "amount")
        changed = "volume"
        name = "PV"
        ia = a.pressure_pa * a.volume_m3
        ib = b.pressure_pa * b.volume_m3
    elif scenario is GasLawScenario.CHARLES:
        v1 = n * R * p.temperature_k / p.pressure_pa
        v2 = n * R * p.target_temperature_k / p.pressure_pa
        a = GasState(p.pressure_pa, v1, p.temperature_k, n)
        b = GasState(p.pressure_pa, v2, p.target_temperature_k, n)
        constants = ("pressure", "amount")
        changed = "temperature"
        name = "V/T"
        ia = a.volume_m3 / a.temperature_k
        ib = b.volume_m3 / b.temperature_k
    else:
        p1 = n * R * p.temperature_k / p.volume_m3
        p2 = n * R * p.target_temperature_k / p.volume_m3
        a = GasState(p1, p.volume_m3, p.temperature_k, n)
        b = GasState(p2, p.volume_m3, p.target_temperature_k, n)
        constants = ("volume", "amount")
        changed = "temperature"
        name = "P/T"
        ia = a.pressure_pa / a.temperature_k
        ib = b.pressure_pa / b.temperature_k
    return GasLawResult(
        p,
        scenario,
        a,
        b,
        constants,
        changed,
        name,
        ia,
        ib,
        f"{scenario.value}: state B has {b.pressure_pa / 1000:.2f} kPa, {b.volume_m3 * 1000:.2f} L, and {b.temperature_k:.2f} K while {', '.join(constants)} remain constant.",
    )
