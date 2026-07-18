from physics_playground.missions.service import MissionProgress, evaluate_run
from physics_playground.subjects.fluids_and_matter.diffusion.missions import evaluate
from physics_playground.subjects.fluids_and_matter.diffusion.physics import (
    DiffusionParameters,
    simulate,
)


def test_diffusion_evaluator_returns_structured_mission_evidence() -> None:
    evaluations = evaluate(simulate(DiffusionParameters()))
    assert all(hasattr(item, "mission_id") and hasattr(item, "completed") for item in evaluations)
    assert {item.mission_id for item in evaluations} == {
        "diffusion_unbiased",
        "diffusion_two_d",
        "diffusion_bias",
        "diffusion_compare",
    }


def test_diffusion_evidence_flows_through_mission_service_after_prediction() -> None:
    progress = MissionProgress(pending_explanations={"diffusion_predict"})
    result = simulate(DiffusionParameters())
    earned = evaluate_run(progress, "diffusion", evaluate(result))
    assert earned == ("diffusion_predict", "diffusion_unbiased", "diffusion_two_d")


def test_diffusion_comparison_and_bias_require_their_actual_runs() -> None:
    progress = MissionProgress(completed={"diffusion_predict"})
    result = simulate(DiffusionParameters(bias_x=0.3))
    earned = evaluate_run(progress, "diffusion", evaluate(result, comparison=True))
    assert "diffusion_bias" in earned
    assert "diffusion_compare" in earned
    assert "diffusion_unbiased" not in earned
