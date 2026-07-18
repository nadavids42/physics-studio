from physics_playground.contracts import MissionEvaluation

from .physics import GasLawScenario


def evaluate(r, comparison=False):
    return (
        MissionEvaluation("gas_boyle", r.scenario is GasLawScenario.BOYLE, "Ran Boyle's law"),
        MissionEvaluation("gas_charles", r.scenario is GasLawScenario.CHARLES, "Ran Charles's law"),
        MissionEvaluation(
            "gas_gay_lussac", r.scenario is GasLawScenario.GAY_LUSSAC, "Ran Gay-Lussac's law"
        ),
        MissionEvaluation("gas_compare", comparison, "Compared gas states"),
    )
