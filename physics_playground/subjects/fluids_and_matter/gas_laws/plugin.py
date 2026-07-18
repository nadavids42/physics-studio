"""SimulationPlugin enrollment adapter for Gas Laws."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from physics_playground.contracts import ContractResult, ModelAssumption, SummaryMetric
from physics_playground.models.expansion import REQUIRED_MODE_REQUIREMENTS
from physics_playground.simulation_plugin import (
    CapabilityImplementation,
    PresentationAdapter,
    SimulationPlugin,
    serialize_parameter_set,
)

from .metadata import SIMULATION
from .physics import GasLawParameters, GasLawResult, simulate

ASSUMPTIONS = (
    ModelAssumption("ideal", "Particles have negligible volume and no intermolecular forces"),
    ModelAssumption("equilibrium", "Each state is uniform and equilibrated"),
)
LIMITATIONS = (
    "Real gases deviate at high pressure and low temperature.",
    "Processes jump between equilibrium states rather than model heat-transfer rates.",
    "No phase changes or chemical reactions.",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class GasLawPluginResult(ContractResult[GasLawParameters]):
    """Shared-runtime envelope retaining the slice's established result."""

    gas: GasLawResult


def run_gas_laws(parameters: GasLawParameters) -> GasLawPluginResult:
    """Adapt the unchanged gas-law calculation to the shared result contract."""

    result = simulate(parameters)
    difference = result.invariant_b - result.invariant_a
    return GasLawPluginResult(
        simulation_id=SIMULATION.id,
        parameters=parameters,
        metrics=(
            SummaryMetric(
                "invariant_difference",
                result.invariant_name + " difference",
                difference,
                display_value=f"{difference:.3g}",
            ),
            SummaryMetric(
                "state_a_pressure_pa", "State A pressure", result.state_a.pressure_pa, "Pa"
            ),
            SummaryMetric("state_a_volume_m3", "State A volume", result.state_a.volume_m3, "m³"),
            SummaryMetric(
                "state_a_temperature_k", "State A temperature", result.state_a.temperature_k, "K"
            ),
            SummaryMetric(
                "state_b_pressure_pa", "State B pressure", result.state_b.pressure_pa, "Pa"
            ),
            SummaryMetric("state_b_volume_m3", "State B volume", result.state_b.volume_m3, "m³"),
            SummaryMetric(
                "state_b_temperature_k", "State B temperature", result.state_b.temperature_k, "K"
            ),
        ),
        assumptions=ASSUMPTIONS,
        outcome_description=result.outcome,
        model_version=SIMULATION.model_version,
        gas=result,
    )


def accessible_summary(result: GasLawPluginResult) -> str:
    return cast(str, result.outcome_description)


PAGE_ENTRYPOINT = "physics_playground.subjects.fluids_and_matter.gas_laws.page.render"

GAS_LAWS_PLUGIN = SimulationPlugin(
    metadata=SIMULATION,
    parameter_type=GasLawParameters,
    result_type=GasLawPluginResult,
    model_runner=run_gas_laws,
    presentation=PresentationAdapter(
        page_entrypoint=PAGE_ENTRYPOINT,
        renderer_entrypoint="physics_playground.canvas.gas_container.build_gas_document",
    ),
    capability_implementations=tuple(
        CapabilityImplementation(capability, PAGE_ENTRYPOINT)
        for requirement in REQUIRED_MODE_REQUIREMENTS
        for capability in requirement.capabilities
    ),
    serialize_notebook_parameters=serialize_parameter_set,
    accessible_summary=accessible_summary,
)
