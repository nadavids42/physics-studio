from physics_playground.contracts import MissionEvaluation
from physics_playground.units import STANDARD_ATMOSPHERE_PA


def evaluate(r, comparison=False):
    return (
        MissionEvaluation(
            "pressure_deep",
            r.parameters.depth_m >= 0.8 * r.parameters.maximum_depth_m,
            "Measured near bottom",
        ),
        MissionEvaluation(
            "pressure_double",
            r.gauge_pressure_pa >= 2 * STANDARD_ATMOSPHERE_PA,
            "Reached two atmospheres gauge",
        ),
        MissionEvaluation("pressure_compare", comparison, "Compared depths"),
    )
