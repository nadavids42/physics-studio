from physics_playground.contracts import MissionEvaluation

from .physics import ForceMode


def evaluate(r, comparison=False):
    return (
        MissionEvaluation("magnetic_zero", r.force_magnitude_n == 0, "Made parallel vectors"),
        MissionEvaluation("magnetic_reverse", r.force_z_n < 0, "Made force point into screen"),
        MissionEvaluation(
            "magnetic_wire", r.mode is ForceMode.CURRENT_WIRE, "Ran current-carrying wire"
        ),
        MissionEvaluation("magnetic_compare", comparison, "Compared perpendicular and parallel"),
    )
