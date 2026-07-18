"""Expansion enrollment manifests for the first mechanics batch."""

from physics_playground.contracts import ModelAssumption
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
)
from physics_playground.registry import SIMULATIONS_BY_ID


def manifest(simulation_id, parameter, result, physics, page, canvas, assumptions, limitations):
    return ExpansionDefinition(
        SIMULATIONS_BY_ID[simulation_id],
        SubjectArea.MECHANICS,
        parameter,
        result,
        physics,
        page,
        canvas,
        REQUIRED_MODE_REQUIREMENTS,
        MISSIONS_BY_SIMULATION[simulation_id],
        tuple(ModelAssumption(str(i), text) for i, text in enumerate(assumptions)),
        tuple(limitations),
    )


MECHANICS_MANIFESTS = (
    manifest(
        "roller_coaster",
        "RollerCoasterParameters",
        "RollerCoasterResult",
        "physics_playground.subjects.mechanics.roller_coaster.physics.simulate",
        "physics_playground.subjects.mechanics.roller_coaster.page.render",
        "physics_playground.subjects.mechanics.canvas.document",
        ("Point-mass car", "Uniform gravity", "Constant optional loss per meter"),
        ("No wheel rotation", "Piecewise-linear track"),
    ),
    manifest(
        "rotational_motion",
        "RotationalParameters",
        "RotationalResult",
        "physics_playground.subjects.mechanics.rotational_motion.physics.simulate",
        "physics_playground.subjects.mechanics.rotational_motion.page.render",
        "physics_playground.subjects.mechanics.canvas.document",
        ("Rigid body", "Fixed axis", "Constant torque"),
        ("No bearing friction", "No deformation"),
    ),
    manifest(
        "inclined_plane",
        "InclinedPlaneParameters",
        "InclinedPlaneResult",
        "physics_playground.subjects.mechanics.inclined_plane.physics.simulate",
        "physics_playground.subjects.mechanics.inclined_plane.page.render",
        "physics_playground.subjects.mechanics.canvas.document",
        ("Rigid block and ramp", "Constant friction coefficients", "Uniform gravity"),
        ("No air resistance", "No deformation"),
    ),
    manifest(
        "torque_levers",
        "LeverParameters",
        "LeverResult",
        "physics_playground.subjects.mechanics.torque_levers.physics.simulate",
        "physics_playground.subjects.mechanics.torque_levers.page.render",
        "physics_playground.subjects.mechanics.canvas.document",
        ("Rigid massless lever", "Frictionless pivot", "Perpendicular forces"),
        ("No beam weight", "Static torque model"),
    ),
    manifest(
        "center_of_mass",
        "CenterOfMassParameters",
        "CenterOfMassResult",
        "physics_playground.subjects.mechanics.center_of_mass.physics.simulate",
        "physics_playground.subjects.mechanics.center_of_mass.page.render",
        "physics_playground.subjects.mechanics.canvas.document",
        ("Point masses", "One-dimensional positions", "Fixed frame"),
        ("No object shapes", "No dynamics"),
    ),
)
