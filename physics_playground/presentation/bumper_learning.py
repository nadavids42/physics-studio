"""Bumper-specific formatting shared by its Analyze and Compare modes."""

from physics_playground.models.collision import CollisionResult


def comparison_measurements(result: CollisionResult) -> dict[str, tuple[str, float]]:
    return {
        "velocity_a": ("Car A final velocity (m/s)", result.velocities_after.car_a_m_s),
        "velocity_b": ("Car B final velocity (m/s)", result.velocities_after.car_b_m_s),
        "energy_lost": ("Energy lost (J)", result.diagnostics.energy_lost_j),
        "impact_time": ("Impact time (s)", result.collision_time_s or 0.0),
    }
