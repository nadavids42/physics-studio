from physics_playground.contracts import MissionEvaluation


def evaluate(r, compared_shapes=False):
    return (
        MissionEvaluation(
            "rotation_spin", abs(r.angular_velocity_rad_s[-1]) >= 10, "Reached 10 rad/s"
        ),
        MissionEvaluation(
            "rotation_energy", r.rotational_kinetic_energy_j[-1] >= 100, "Reached 100 J"
        ),
        MissionEvaluation("rotation_shape_compare", compared_shapes, "Two inertia models compared"),
    )
