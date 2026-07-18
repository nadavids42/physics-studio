import math

import pytest

from physics_playground.subjects.fluids_and_matter.gas_laws.physics import (
    GAS_CONSTANT_J_MOL_K,
    GasLawParameters,
    GasLawScenario,
    celsius_to_kelvin,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_ideal_gas_state_satisfies_pv_equals_nrt() -> None:
    result = simulate(GasLawParameters())
    assert result.state_a.pressure_pa * result.state_a.volume_m3 == pytest.approx(
        result.state_a.amount_mol * GAS_CONSTANT_J_MOL_K * result.state_a.temperature_k
    )
    assert result.state_a.ideal_residual_j == pytest.approx(0.0, abs=1e-12)


def test_boyle_compression_conserves_pv_and_doubles_pressure() -> None:
    result = simulate(
        GasLawParameters(scenario=GasLawScenario.BOYLE, volume_m3=0.024, target_volume_m3=0.012)
    )
    assert result.invariant_a == pytest.approx(result.invariant_b)
    assert result.state_b.pressure_pa == pytest.approx(2 * result.state_a.pressure_pa)
    assert result.state_a.temperature_k == result.state_b.temperature_k


def test_charles_law_conserves_volume_over_temperature() -> None:
    result = simulate(
        GasLawParameters(
            scenario=GasLawScenario.CHARLES, temperature_k=250, target_temperature_k=500
        )
    )
    assert result.invariant_a == pytest.approx(result.invariant_b)
    assert result.state_b.volume_m3 == pytest.approx(2 * result.state_a.volume_m3)
    assert result.state_a.pressure_pa == result.state_b.pressure_pa


def test_gay_lussac_law_conserves_pressure_over_temperature() -> None:
    result = simulate(
        GasLawParameters(
            scenario=GasLawScenario.GAY_LUSSAC, temperature_k=250, target_temperature_k=500
        )
    )
    assert result.invariant_a == pytest.approx(result.invariant_b)
    assert result.state_b.pressure_pa == pytest.approx(2 * result.state_a.pressure_pa)
    assert result.state_a.volume_m3 == result.state_b.volume_m3


def test_standard_molar_state_is_about_one_atmosphere() -> None:
    result = simulate(GasLawParameters(amount_mol=1, volume_m3=0.022414, temperature_k=273.15))
    assert result.state_a.pressure_pa / 1000 == pytest.approx(101.325, rel=2e-3)


def test_celsius_conversion_and_absolute_zero_validation() -> None:
    assert celsius_to_kelvin(0) == pytest.approx(273.15)
    with pytest.raises(PhysicsValidationError, match="absolute zero"):
        celsius_to_kelvin(-273.15)


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount_mol", 0),
        ("pressure_pa", 0),
        ("volume_m3", 0),
        ("target_volume_m3", -1),
        ("temperature_k", 0),
        ("target_temperature_k", -1),
        ("amount_mol", math.inf),
    ],
)
def test_invalid_and_nonfinite_parameters_are_rejected(field: str, value: float) -> None:
    values = (
        GasLawParameters().__dict__
        if hasattr(GasLawParameters(), "__dict__")
        else {
            name: getattr(GasLawParameters(), name)
            for name in GasLawParameters.__dataclass_fields__
        }
    )
    values[field] = value
    with pytest.raises(PhysicsValidationError):
        simulate(GasLawParameters(**values))


def test_identical_inputs_are_deterministic() -> None:
    parameters = GasLawParameters(scenario=GasLawScenario.BOYLE)
    assert simulate(parameters) == simulate(parameters)
