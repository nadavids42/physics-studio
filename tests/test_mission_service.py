from physics_playground.contracts import MissionEvaluation
from physics_playground.missions.definitions import (
    MISSION_DEFINITIONS,
    MISSIONS_BY_SIMULATION,
    MissionType,
)
from physics_playground.missions.service import (
    MissionProgress,
    evaluate_run,
    hint_for,
    overall_percentage,
    summary,
)


def test_all_existing_achievements_are_preserved():
    assert len(MISSION_DEFINITIONS) >= 25
    assert {
        "tunnel_predict",
        "pend_predict",
        "orbit_predict",
        "cannon_predict",
        "spring_predict",
        "chaos_predict",
        "collision_predict",
    } <= set(MISSION_DEFINITIONS)


def test_three_mission_types_are_present():
    assert {item.category for item in MISSION_DEFINITIONS.values()} == set(MissionType)


def test_prediction_is_not_awarded_before_experiment_run():
    progress = MissionProgress()
    progress.pending_explanations.add("collision_predict")
    assert "collision_predict" not in progress.completed


def test_pending_prediction_is_awarded_on_run():
    progress = MissionProgress(pending_explanations={"collision_predict"})
    earned = evaluate_run(progress, "bumper_cars", ())
    assert earned == ("collision_predict",)
    assert "collision_predict" in progress.completed


def test_observational_mission_requires_positive_evaluation_and_prerequisite():
    progress = MissionProgress()
    evaluation = (MissionEvaluation("collision_swap", True, "evidence"),)
    assert evaluate_run(progress, "bumper_cars", evaluation) == ()
    progress.pending_explanations.add("collision_predict")
    evaluate_run(progress, "bumper_cars", ())
    assert evaluate_run(progress, "bumper_cars", evaluation) == ("collision_swap",)


def test_progressive_hints_advance_after_failed_runs():
    progress = MissionProgress(completed={"collision_predict"})
    first = hint_for(progress, "collision_swap")
    evaluate_run(progress, "bumper_cars", (MissionEvaluation("collision_swap", False, "miss"),))
    second = hint_for(progress, "collision_swap")
    assert first != second


def test_secret_achievements_exist_and_remain_in_totals():
    hidden = [item for item in MISSION_DEFINITIONS.values() if item.hidden]
    assert len(hidden) >= 3
    assert all(item in MISSIONS_BY_SIMULATION[item.simulation_id] for item in hidden)


def test_per_simulation_and_overall_summaries():
    progress = MissionProgress(completed={"collision_predict", "collision_swap"})
    status = summary(progress, "bumper_cars")
    assert status.earned == 2 and status.total == 4 and status.percentage == 0.5
    assert overall_percentage(progress) == 2 / len(MISSION_DEFINITIONS)
