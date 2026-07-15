"""Authoritative assumptions and limitations for simulation models."""

from __future__ import annotations

from dataclasses import dataclass

from physics_playground.contracts import ModelAssumption


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    simulation_id: str
    assumptions: tuple[ModelAssumption, ...]
    limitations: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.simulation_id:
            raise ValueError("Model metadata requires a simulation ID.")
        ids = [item.id for item in self.assumptions]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"{self.simulation_id} assumptions require unique IDs.")
        if any(not item.statement.strip() for item in self.assumptions):
            raise ValueError(f"{self.simulation_id} contains an empty assumption.")

    @property
    def assumption_statements(self) -> tuple[str, ...]:
        return tuple(item.statement for item in self.assumptions)


def _metadata(
    simulation_id: str,
    assumptions: tuple[str, ...],
    limitations: tuple[str, ...] = (),
) -> ModelMetadata:
    return ModelMetadata(
        simulation_id,
        tuple(ModelAssumption(f"assumption_{index}", statement) for index, statement in enumerate(assumptions, 1)),
        limitations,
    )


PROJECTILE_MODEL_METADATA = ModelMetadata(
    "cannonball",
    (
        ModelAssumption(
            "flat_ground",
            "Launch and landing ground are flat and stationary.",
            "Range is measured on one horizontal plane; planetary curvature and rotation are excluded.",
        ),
        ModelAssumption(
            "constant_gravity",
            "Gravity is uniform and points straight down.",
            "The same gravitational acceleration applies throughout the trajectory.",
        ),
        ModelAssumption(
            "point_projectile",
            "The projectile is treated as a point mass.",
            "Size, shape, lift, and spin are not resolved.",
        ),
    ),
    (
        "Wind, lift, spin, and changing air density are omitted.",
        "The drag coefficient combines shape, area, and air density into one constant.",
        "Fixed-step RK4 is accurate but not adaptive.",
    ),
)


MODEL_METADATA = {
    item.simulation_id: item
    for item in (
        _metadata("gas_laws", ("Ideal-gas particles", "Uniform equilibrium states", "No phase change or chemical reaction")),
        _metadata("diffusion", ("Independent seeded steps", "Fixed step size and timestep", "No boundaries or particle interactions")),
        _metadata("buoyancy", ("Uniform object and fluid densities", "Static equilibrium or fully submerged state", "No surface tension or drag dynamics")),
        _metadata("fluid_pressure", ("Fluid at rest", "Constant density and gravity", "Uniform surface pressure")),
        _metadata("magnetic_forces", ("Uniform magnetic field", "Nonrelativistic point charge or straight wire", "Vectors represented in the screen plane")),
        _metadata("electric_fields", ("Ideal stationary point charges", "Vacuum Coulomb law", "Minimum-distance singularity exclusion for visualization")),
        _metadata("reflection_refraction", ("Geometric-optics rays", "Flat boundary between uniform isotropic media", "No absorption or dispersion")),
        _metadata("thin_lenses", ("Thin-lens approximation", "Paraxial rays", "Single ideal lens in air")),
        _metadata("doppler_effect", ("Stationary uniform sound medium", "Classical subsonic motion", "One-dimensional source and observer")),
        _metadata("wave_interference", ("Linear superposition", "Ideal sinusoidal traveling waves", "No damping, reflection, or dispersion")),
        _metadata("roller_coaster", ("Point-mass car", "Uniform gravity", "Piecewise-linear track and optional constant loss per meter")),
        _metadata("rotational_motion", ("Rigid body", "Fixed rotation axis", "Constant applied torque")),
        _metadata("inclined_plane", ("Rigid block and ramp", "Constant friction coefficients", "Uniform gravitational field")),
        _metadata("torque_levers", ("Rigid massless lever", "Frictionless pivot", "Forces perpendicular to the beam")),
        _metadata("center_of_mass", ("Objects represented by point masses", "One-dimensional positions", "Fixed reference frame")),
        _metadata("bumper_cars", ("One-dimensional motion", "Instantaneous collision", "No external horizontal force")),
        PROJECTILE_MODEL_METADATA,
        _metadata("boing", ("Hooke's law", "Point mass and massless spring", "Linear damping where enabled")),
        _metadata("pendulum", ("Point bob and rigid massless rope", "Fixed gravity", "No air or pivot friction")),
        _metadata("orbital_gravity", ("Fixed central mass", "Test-particle planet", "No drag or third-body perturbations")),
        _metadata("earth_tunnel", ("Spherical planet", "Vacuum tunnel", "No planetary rotation")),
        _metadata("double_pendulum", ("Point masses and rigid rods", "No damping", "Ideal frictionless pivots")),
    )
}

for _item in MODEL_METADATA.values():
    _item.validate()


def metadata_for(simulation_id: str) -> ModelMetadata:
    try:
        return MODEL_METADATA[simulation_id]
    except KeyError as error:
        raise KeyError(f"No model metadata registered for {simulation_id!r}.") from error

