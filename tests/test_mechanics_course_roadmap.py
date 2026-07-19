from __future__ import annotations

from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.subjects.mechanics.course_roadmap import (
    INTRODUCTORY_MECHANICS_LESSONS,
    INTRODUCTORY_MECHANICS_UNITS,
    validate_mechanics_roadmap,
)

SIMULATION_IDS = {simulation.id for simulation in SIMULATION_REGISTRY}


def test_mechanics_roadmap_references_are_valid() -> None:
    validate_mechanics_roadmap(simulation_ids=SIMULATION_IDS)


def test_mechanics_roadmap_has_a_coherent_course_scale() -> None:
    assert len(INTRODUCTORY_MECHANICS_UNITS) == 8
    assert len(INTRODUCTORY_MECHANICS_LESSONS) == 24
    assert all(len(unit.lessons) == 3 for unit in INTRODUCTORY_MECHANICS_UNITS)
    assert sum(lesson.estimated_minutes for lesson in INTRODUCTORY_MECHANICS_LESSONS) == 1330


def test_every_lesson_has_objectives_assessment_and_mastery_evidence() -> None:
    for lesson in INTRODUCTORY_MECHANICS_LESSONS:
        objective_ids = {objective.id for objective in lesson.objectives}
        assert len(objective_ids) >= 2
        assert lesson.worked_examples
        assert lesson.assessments
        assert lesson.misconceptions
        assert lesson.mastery_evidence
        assert all(
            set(assessment.objective_ids) <= objective_ids for assessment in lesson.assessments
        )


def test_simulations_are_used_selectively_and_only_from_mechanics() -> None:
    used = {
        activity.simulation_id
        for lesson in INTRODUCTORY_MECHANICS_LESSONS
        for activity in lesson.simulation_activities
    }
    assert used == {
        "bumper_cars",
        "cannonball",
        "center_of_mass",
        "inclined_plane",
        "orbital_gravity",
        "roller_coaster",
        "rotational_motion",
        "torque_levers",
    }
    assert any(not lesson.simulation_activities for lesson in INTRODUCTORY_MECHANICS_LESSONS)
