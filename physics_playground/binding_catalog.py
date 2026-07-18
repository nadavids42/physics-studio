"""Registry of simulations ready for reusable preset and lesson integration."""

from physics_playground.binding_models import (
    ExpectedMetric,
    MetricDefinition,
    SimulationBinding,
    SimulationPreset,
)
from physics_playground.model_metadata import PROJECTILE_MODEL_METADATA
from physics_playground.models.projectile import (
    PROJECTILE_MODEL_VERSION,
    ProjectileParameters,
    ProjectileResult,
    simulate_projectile,
)

PROJECTILE_BINDING = SimulationBinding(
    simulation_id="cannonball",
    parameter_model=ProjectileParameters,
    result_model=ProjectileResult,
    model_version=PROJECTILE_MODEL_VERSION,
    runner=simulate_projectile,
    metadata=PROJECTILE_MODEL_METADATA,
    metrics=(
        MetricDefinition("range", "Range", "m"),
        MetricDefinition("maximum_height", "Maximum height", "m"),
        MetricDefinition("flight_time", "Flight time", "s"),
        MetricDefinition("impact_speed", "Impact speed", "m/s"),
        MetricDefinition("energy_lost", "Mechanical energy lost", "J"),
    ),
)


PROJECTILE_WORKED_EXAMPLE_PRESET = SimulationPreset(
    id="projectile_no_drag_20ms_35deg",
    simulation_id="cannonball",
    title="Launch at 20 m/s and 35° on Earth",
    parameters=ProjectileParameters(20.0, 35.0).to_dict(),
    model_version=PROJECTILE_MODEL_VERSION,
    expected_metrics=(
        ExpectedMetric("range", 38.31570319208596, absolute_tolerance=1e-9),
        ExpectedMetric("maximum_height", 6.707236051726107, absolute_tolerance=0.01),
        ExpectedMetric("flight_time", 2.3387418403712377, absolute_tolerance=1e-9),
        ExpectedMetric("impact_speed", 20.0, absolute_tolerance=1e-9),
        ExpectedMetric("energy_lost", 0.0, absolute_tolerance=1e-9),
    ),
)


SIMULATION_BINDINGS = {PROJECTILE_BINDING.simulation_id: PROJECTILE_BINDING}
SIMULATION_PRESETS = {PROJECTILE_WORKED_EXAMPLE_PRESET.id: PROJECTILE_WORKED_EXAMPLE_PRESET}


def binding_for(simulation_id: str) -> SimulationBinding:
    try:
        return SIMULATION_BINDINGS[simulation_id]
    except KeyError as error:
        raise KeyError(f"No simulation binding registered for {simulation_id!r}.") from error


def preset_for(preset_id: str) -> SimulationPreset:
    try:
        return SIMULATION_PRESETS[preset_id]
    except KeyError as error:
        raise KeyError(f"No simulation preset registered for {preset_id!r}.") from error
