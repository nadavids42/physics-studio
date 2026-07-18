from physics_playground.contracts import MissionEvaluation


def evaluate(result):
    p = result.parameters
    return (
        MissionEvaluation("com_origin", abs(result.center_of_mass_m) < 0.1, "Center near origin"),
        MissionEvaluation("com_three", p.mass_3_kg > 0, "Three masses used"),
    )
