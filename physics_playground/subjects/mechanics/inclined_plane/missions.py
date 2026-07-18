from physics_playground.contracts import MissionEvaluation


def evaluate(result):
    p = result.parameters
    return (
        MissionEvaluation("incline_slide", result.moving, "Block moved"),
        MissionEvaluation(
            "incline_threshold",
            abs(p.angle_deg - result.critical_angle_deg) < 2,
            "Near critical angle",
        ),
    )
