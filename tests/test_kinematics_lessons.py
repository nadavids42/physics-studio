"""Coverage, progression, science, and evidence tests for kinematics lessons."""

from physics_playground.education.catalog import ASSESSMENTS_BY_ID
from physics_playground.education.models import (
    CheckpointQuestion,
    MisconceptionCallout,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.education.progress import PathwayProgress
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON
from physics_playground.subjects.mechanics.kinematics_lessons import KINEMATICS_LESSONS


def test_kinematics_prerequisites_form_one_progression_from_lesson_one() -> None:
    expected = (
        "m01-measurement-models",
        KINEMATICS_LESSONS[0].id,
        KINEMATICS_LESSONS[1].id,
    )
    assert tuple(lesson.prerequisites[0].reference_id for lesson in KINEMATICS_LESSONS) == expected
    assert any(
        prerequisite.reference_id == KINEMATICS_LESSONS[-1].id
        for prerequisite in CANNONBALL_LESSON.prerequisites
    )


def test_sequence_uses_multiple_simulations_and_complete_scientific_components() -> None:
    assert {lesson.simulation_ids[0] for lesson in KINEMATICS_LESSONS} == {
        "bumper_cars",
        "cannonball",
        "inclined_plane",
    }
    for lesson in KINEMATICS_LESSONS:
        components = [item for section in lesson.sections for item in section.components]
        assert any(isinstance(item, WorkedExample) for item in components)
        assert any(isinstance(item, MisconceptionCallout) for item in components)
        assert any(isinstance(item, CheckpointQuestion) for item in components)
        assert any(isinstance(item, SimulationActivity) for item in components)
        assert "m/s" in " ".join(
            item.unit_check for item in components if isinstance(item, WorkedExample)
        )


def test_every_objective_has_component_evidence_and_every_checkpoint_has_scoring() -> None:
    for lesson in KINEMATICS_LESSONS:
        objective_ids = {objective.id for objective in lesson.objectives}
        covered: set[str] = set()
        for section in lesson.sections:
            for component in section.components:
                if isinstance(component, SimulationActivity | CheckpointQuestion):
                    covered.update(component.objective_ids)
                if isinstance(component, CheckpointQuestion):
                    definition = ASSESSMENTS_BY_ID[component.id]
                    assert definition.lesson_id == lesson.id
                    assert set(definition.objective_ids) == set(component.objective_ids)
        assert covered == objective_ids


def test_required_misconceptions_are_explicitly_diagnosed() -> None:
    text = " ".join(
        item.misconception
        for lesson in (*KINEMATICS_LESSONS, CANNONBALL_LESSON)
        for section in lesson.sections
        for item in section.components
        if isinstance(item, MisconceptionCallout)
    ).lower()
    for phrase in (
        "negative velocity means",
        "zero velocity means zero acceleration",
        "heavier projectiles fall faster",
        "acceleration always points in the direction of motion",
        "45° launch always",
    ):
        assert phrase in text


def test_visiting_or_opening_a_simulation_cannot_complete_a_lesson() -> None:
    for lesson in KINEMATICS_LESSONS:
        progress = PathwayProgress(lesson.id)
        assert not progress.completed
        assert not progress.completed_activity_ids
        assert not progress.mastered_objective_ids
        evidence_activities = [item for item in lesson.activity_sequence if item.evidence_prompt]
        assert evidence_activities
        for activity in evidence_activities:
            try:
                progress.save_activity_response(
                    activity.id,
                    " ",
                    required_activity_ids=tuple(item.id for item in lesson.activity_sequence),
                    required_checkpoint_ids=(),
                )
            except ValueError:
                pass
            else:
                raise AssertionError("Blank evidence must not complete an activity")
