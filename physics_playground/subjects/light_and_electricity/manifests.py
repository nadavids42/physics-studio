from physics_playground.contracts import ModelAssumption
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
)
from physics_playground.registry import SIMULATIONS_BY_ID


def make(sim, param, result, physics, page, assumptions, limitations):
    return ExpansionDefinition(
        SIMULATIONS_BY_ID[sim],
        SubjectArea.LIGHT_AND_ELECTRICITY,
        param,
        result,
        physics,
        page,
        "physics_playground.canvas.ray_diagram.build_ray_diagram",
        REQUIRED_MODE_REQUIREMENTS,
        MISSIONS_BY_SIMULATION[sim],
        tuple(ModelAssumption(str(i), x) for i, x in enumerate(assumptions)),
        tuple(limitations),
    )


OPTICS_MANIFESTS = (
    make(
        "reflection_refraction",
        "ReflectionRefractionParameters",
        "ReflectionRefractionResult",
        "physics_playground.subjects.light_and_electricity.reflection_refraction.physics.simulate",
        "physics_playground.subjects.light_and_electricity.reflection_refraction.page.render",
        ("Geometric rays", "Flat interface", "Uniform media"),
        ("No dispersion", "No polarization"),
    ),
    make(
        "thin_lenses",
        "ThinLensParameters",
        "ThinLensResult",
        "physics_playground.subjects.light_and_electricity.thin_lenses.physics.simulate",
        "physics_playground.subjects.light_and_electricity.thin_lenses.page.render",
        ("Thin lens", "Paraxial rays", "Ideal lens"),
        ("No aberration", "Single lens in air"),
    ),
)
ELECTRIC_FIELD_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["electric_fields"],
    SubjectArea.LIGHT_AND_ELECTRICITY,
    "ElectricFieldParameters",
    "ElectricFieldResult",
    "physics_playground.subjects.light_and_electricity.electric_fields.physics.simulate",
    "physics_playground.subjects.light_and_electricity.electric_fields.page.render",
    "physics_playground.canvas.vector_field.build_vector_field_document",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["electric_fields"],
    (
        ModelAssumption("point", "Ideal point charges"),
        ModelAssumption("static", "Electrostatic vacuum model"),
    ),
    ("No conductors or materials", "Singular points excluded"),
)
MAGNETIC_FORCE_MANIFEST = ExpansionDefinition(
    SIMULATIONS_BY_ID["magnetic_forces"],
    SubjectArea.LIGHT_AND_ELECTRICITY,
    "MagneticForceParameters",
    "MagneticForceResult",
    "physics_playground.subjects.light_and_electricity.magnetic_forces.physics.simulate",
    "physics_playground.subjects.light_and_electricity.magnetic_forces.page.render",
    "physics_playground.canvas.vector_diagram.build_vector_direction_document",
    REQUIRED_MODE_REQUIREMENTS,
    MISSIONS_BY_SIMULATION["magnetic_forces"],
    (
        ModelAssumption("uniform", "Uniform magnetic field"),
        ModelAssumption("planar", "Input vectors lie in screen plane"),
    ),
    ("No electric field or radiation", "Nonrelativistic point charge"),
)
LIGHT_ELECTRICITY_MANIFESTS = (*OPTICS_MANIFESTS, ELECTRIC_FIELD_MANIFEST, MAGNETIC_FORCE_MANIFEST)
