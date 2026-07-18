from physics_playground.contracts import ModelAssumption
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
)
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.subjects.fluids_and_matter.gas_laws.plugin import GAS_LAWS_PLUGIN


def make(sim, param, result, physics, page, canvas, assumptions, limitations):
    return ExpansionDefinition(
        SIMULATIONS_BY_ID[sim],
        SubjectArea.FLUIDS_AND_MATTER,
        param,
        result,
        physics,
        page,
        canvas,
        REQUIRED_MODE_REQUIREMENTS,
        MISSIONS_BY_SIMULATION[sim],
        tuple(ModelAssumption(str(i), x) for i, x in enumerate(assumptions)),
        tuple(limitations),
    )


FLUID_MANIFESTS = (
    make(
        "diffusion",
        "DiffusionParameters",
        "DiffusionResult",
        "physics_playground.subjects.fluids_and_matter.diffusion.physics.simulate",
        "physics_playground.subjects.fluids_and_matter.diffusion.page.render",
        "physics_playground.canvas.diffusion_player.build_diffusion_document",
        ("Independent seeded steps", "Fixed step size and timestep", "Noninteracting particles"),
        ("No boundaries", "No molecular collisions", "Finite samples fluctuate"),
    ),
    make(
        "gas_laws",
        "GasLawParameters",
        "GasLawResult",
        "physics_playground.subjects.fluids_and_matter.gas_laws.physics.simulate",
        GAS_LAWS_PLUGIN.presentation.page_entrypoint,
        GAS_LAWS_PLUGIN.presentation.renderer_entrypoint,
        ("Ideal gas", "Equilibrium states", "Constant gas amount"),
        ("No real-gas corrections", "No phase changes"),
    ),
    make(
        "buoyancy",
        "BuoyancyParameters",
        "BuoyancyResult",
        "physics_playground.subjects.fluids_and_matter.buoyancy.physics.simulate",
        "physics_playground.subjects.fluids_and_matter.buoyancy.page.render",
        "physics_playground.canvas.fluid_container.build_fluid_document",
        ("Uniform density", "Archimedes principle", "Static final state"),
        ("No drag dynamics", "No surface tension"),
    ),
    make(
        "fluid_pressure",
        "FluidPressureParameters",
        "FluidPressureResult",
        "physics_playground.subjects.fluids_and_matter.fluid_pressure.physics.simulate",
        "physics_playground.subjects.fluids_and_matter.fluid_pressure.page.render",
        "physics_playground.canvas.fluid_container.build_fluid_document",
        ("Hydrostatic fluid", "Uniform density", "Constant gravity"),
        ("No compressibility", "No fluid acceleration"),
    ),
)
