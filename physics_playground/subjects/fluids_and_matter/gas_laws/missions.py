from physics_playground.contracts import MissionEvaluation

from .physics import GasLawResult, GasLawScenario


def evaluate(result: GasLawResult, comparison: bool = False) -> tuple[MissionEvaluation, ...]:
    return (
        MissionEvaluation("gas_boyle", result.scenario is GasLawScenario.BOYLE, "Ran Boyle's law"),
        MissionEvaluation(
            "gas_charles", result.scenario is GasLawScenario.CHARLES, "Ran Charles's law"
        ),
        MissionEvaluation(
            "gas_gay_lussac",
            result.scenario is GasLawScenario.GAY_LUSSAC,
            "Ran Gay-Lussac's law",
        ),
        MissionEvaluation("gas_compare", comparison, "Compared gas states"),
    )
