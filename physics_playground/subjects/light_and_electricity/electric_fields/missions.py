from physics_playground.contracts import MissionEvaluation


def evaluate(r, comparison=False):
    signs = {1 if c.charge_c > 0 else -1 for c in r.parameters.charges}
    return (
        MissionEvaluation("field_dipole", len(signs) == 2, "Used positive and negative charges"),
        MissionEvaluation(
            "field_zero_force", r.force_magnitude_n < 1e-8, "Made a nearly force-free test point"
        ),
        MissionEvaluation("field_compare", comparison, "Compared like and opposite charges"),
    )
