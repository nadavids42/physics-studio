"""Expansion enrollment manifests for the first mechanics batch."""

from physics_playground.contracts import ModelAssumption
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
)
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.subjects.mechanics.cannonball.plugin import CANNONBALL_PLUGIN


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
        "earth_tunnel",
        "TunnelParameters",
        "TunnelResult",
        "physics_playground.subjects.mechanics.earth_tunnel.physics.simulate_tunnel",
        "physics_playground.subjects.mechanics.earth_tunnel.page.render",
        "physics_playground.subjects.mechanics.earth_tunnel.scene.build_tunnel_canvas",
        ("Spherical planet", "Frictionless straight tunnel", "Newtonian gravity"),
        ("No rotation or atmosphere", "Idealized interior density models"),
    ),
    manifest(
        "bumper_cars",
        "CollisionParameters",
        "CollisionResult",
        "physics_playground.subjects.mechanics.bumper_cars.physics.simulate_collision",
        "physics_playground.subjects.mechanics.bumper_cars.page.render",
        "physics_playground.subjects.mechanics.bumper_cars.scene.build_bumper_canvas",
        ("One-dimensional collision", "Constant restitution", "No external impulse"),
        ("Rigid point-like cars", "No rotation or deformation dynamics"),
    ),
    manifest(
        "orbital_gravity",
        "OrbitParameters",
        "OrbitResult",
        "physics_playground.subjects.mechanics.orbital_gravity.physics.simulate_orbit",
        "physics_playground.subjects.mechanics.orbital_gravity.page.render",
        "physics_playground.subjects.mechanics.orbital_gravity.scene.build_orbit_canvas",
        ("Point-mass orbiting body", "Fixed central mass", "Newtonian inverse-square gravity"),
        ("Two-dimensional motion", "No perturbing bodies or relativistic effects"),
    ),
    manifest(
        "cannonball",
        "ProjectileParameters",
        "ProjectileResult",
        "physics_playground.subjects.mechanics.cannonball.physics.simulate_projectile",
        CANNONBALL_PLUGIN.presentation.page_entrypoint,
        CANNONBALL_PLUGIN.presentation.renderer_entrypoint,
        ("Point-mass projectile", "Uniform gravity", "Level launch and landing surface"),
        ("Two-dimensional motion", "Quadratic drag uses a fixed atmosphere model"),
    ),
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
