from physics_playground.contracts import MissionEvaluation


def evaluate(r, comparison=False):
    return (
        MissionEvaluation("lens_real", r.real_image is True, "Made a real image"),
        MissionEvaluation("lens_virtual", r.real_image is False, "Made a virtual image"),
        MissionEvaluation("lens_compare", comparison, "Compared lens types"),
    )
