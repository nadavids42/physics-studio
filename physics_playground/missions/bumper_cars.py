"""Side-effect-free mission rules for completed Bumper Cars trials."""

from physics_playground.contracts import MissionEvaluation
from physics_playground.models.collision import CollisionResult


def evaluate_bumper_missions(result: CollisionResult) -> tuple[MissionEvaluation, ...]:
    """Evaluate observational badges after a user launches the experiment."""

    if not result.collided:
        return ()
    p = result.parameters
    after = result.velocities_after
    mass_ratio_close = abs(p.mass_a_kg - p.mass_b_kg) / ((p.mass_a_kg + p.mass_b_kg) / 2.0) < 0.15
    return (
        MissionEvaluation(
            "collision_swap",
            p.restitution > 0.95
            and abs(p.velocity_b_m_s) < 0.3
            and mass_ratio_close
            and abs(after.car_a_m_s) < 0.3,
            "Use nearly equal masses and bouncy bumpers to swap velocities.",
            {"velocity_a_after_m_s": after.car_a_m_s},
        ),
        MissionEvaluation(
            "collision_stop",
            p.restitution < 0.05 and abs(result.diagnostics.momentum_before_kg_m_s) < 0.5,
            "Use sticky bumpers and balance the incoming momentum.",
            {"momentum_before_kg_m_s": result.diagnostics.momentum_before_kg_m_s},
        ),
        MissionEvaluation(
            "collision_bounce",
            p.restitution > 0.95 and p.mass_a_kg < 0.5 * p.mass_b_kg and after.car_a_m_s < -0.3,
            "Bounce a light Car A backward from a much heavier Car B.",
            {"velocity_a_after_m_s": after.car_a_m_s},
        ),
    )
