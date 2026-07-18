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
PENDULUM_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["pendulum"],
    SubjectArea.WAVES_AND_OSCILLATIONS,
    "PendulumParameters",
    "PendulumResult",
    "physics_playground.subjects.waves_and_oscillations.pendulum.physics.simulate_pendulum",
    "physics_playground.subjects.waves_and_oscillations.pendulum.page.render",
    "physics_playground.subjects.waves_and_oscillations.pendulum.scene.build_pendulum_canvas",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["pendulum"],
    (
        ModelAssumption("point_mass", "Point-mass bob on a massless rigid link"),
        ModelAssumption("uniform_gravity", "Uniform gravitational field"),
    ),
    ("No pivot friction or air resistance", "Motion remains planar"),
    tests=TestRequirements(numerical_convergence_test=True),
)
BOING_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["boing"],
    SubjectArea.WAVES_AND_OSCILLATIONS,
    "SpringParameters",
    "SpringResult",
    "physics_playground.subjects.waves_and_oscillations.boing.physics.simulate_spring",
    "physics_playground.subjects.waves_and_oscillations.boing.page.render",
    "physics_playground.subjects.waves_and_oscillations.boing.scene.build_boing_canvas",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["boing"],
    (
        ModelAssumption("hooke", "Linear Hooke-law spring"),
        ModelAssumption("point_mass", "Point mass with one-dimensional motion"),
    ),
    ("No spring mass", "Linear damping and sinusoidal drive only"),
    tests=TestRequirements(numerical_convergence_test=True),
)
WAVES_MANIFESTS = (
    WAVE_INTERFERENCE_MANIFEST,
    DOPPLER_EFFECT_MANIFEST,
    PENDULUM_MANIFEST,
    BOING_MANIFEST,
)
