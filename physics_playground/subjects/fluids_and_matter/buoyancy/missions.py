from physics_playground.contracts import MissionEvaluation

from .physics import BuoyancyState


def evaluate(r, comparison=False):
    return (
        MissionEvaluation("buoy_float", r.state is BuoyancyState.FLOATING, "Made an object float"),
        MissionEvaluation(
            "buoy_neutral", r.state is BuoyancyState.NEUTRAL, "Matched object and fluid density"
        ),
        MissionEvaluation("buoy_compare", comparison, "Compared fluids"),
    )
