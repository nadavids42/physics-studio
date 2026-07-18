from physics_playground.contracts import ModelAssumption
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
    TestRequirements,
)
from physics_playground.registry import SIMULATIONS_BY_ID

WAVE_INTERFERENCE_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["wave_interference"],
    SubjectArea.WAVES_AND_OSCILLATIONS,
    "WaveInterferenceParameters",
    "WaveInterferenceResult",
    "physics_playground.subjects.waves_and_oscillations.wave_interference.physics.simulate",
    "physics_playground.subjects.waves_and_oscillations.wave_interference.page.render",
    "physics_playground.canvas.scalar_field.build_scalar_field_document",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["wave_interference"],
    (
        ModelAssumption("linear", "Linear superposition"),
        ModelAssumption("ideal", "Ideal sinusoidal traveling waves"),
    ),
    ("No boundaries or reflection", "No damping or dispersion"),
    tests=TestRequirements(numerical_convergence_test=False),
)
DOPPLER_EFFECT_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["doppler_effect"],
    SubjectArea.WAVES_AND_OSCILLATIONS,
    "DopplerParameters",
    "DopplerResult",
    "physics_playground.subjects.waves_and_oscillations.doppler_effect.physics.simulate",
    "physics_playground.subjects.waves_and_oscillations.doppler_effect.page.render",
    "physics_playground.canvas.wavefronts.build_wavefront_document",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["doppler_effect"],
    (
        ModelAssumption("medium", "Stationary uniform medium"),
        ModelAssumption("subsonic", "Classical subsonic motion"),
    ),
    ("No wind or reflections", "One-dimensional geometry"),
    tests=TestRequirements(numerical_convergence_test=False),
)
WAVES_MANIFESTS = (WAVE_INTERFERENCE_MANIFEST, DOPPLER_EFFECT_MANIFEST)
