"""SimulationPlugin enrollment for Cannonball."""

from __future__ import annotations

from typing import cast

from physics_playground.models.expansion import REQUIRED_MODE_REQUIREMENTS
from physics_playground.simulation_cache import cached_projectile
from physics_playground.simulation_plugin import (
    CapabilityImplementation,
    PresentationAdapter,
    SimulationPlugin,
    serialize_parameter_set,
)

from .metadata import SIMULATION
from .physics import ProjectileParameters, ProjectileResult


def run_cannonball(parameters: ProjectileParameters) -> ProjectileResult:
    return cast(ProjectileResult, cached_projectile(parameters))


def accessible_summary(result: ProjectileResult) -> str:
    landing = "landed" if result.landed else "did not land"
    return (
        f"The projectile {landing} after traveling {result.range_m:.1f} meters horizontally "
        f"and reaching {result.maximum_height_m:.1f} meters high."
    )


PAGE_ENTRYPOINT = "physics_playground.subjects.mechanics.cannonball.page.render"

CANNONBALL_PLUGIN = SimulationPlugin(
    metadata=SIMULATION,
    parameter_type=ProjectileParameters,
    result_type=ProjectileResult,
    model_runner=run_cannonball,
    presentation=PresentationAdapter(
        page_entrypoint=PAGE_ENTRYPOINT,
        renderer_entrypoint=(
            "physics_playground.subjects.mechanics.cannonball.scene.build_cannon_canvas"
        ),
    ),
    capability_implementations=tuple(
        CapabilityImplementation(capability, PAGE_ENTRYPOINT)
        for requirement in REQUIRED_MODE_REQUIREMENTS
        for capability in requirement.capabilities
    ),
    serialize_notebook_parameters=serialize_parameter_set,
    accessible_summary=accessible_summary,
)
