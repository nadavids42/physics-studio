"""Scientific-content and flow checks for Mechanics lesson 1."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from physics_playground.education.models import (
    CheckpointQuestion,
    MisconceptionCallout,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.education.progress import PathwayProgress
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key
from physics_playground.subjects.mechanics.course_roadmap import (
    INTRODUCTORY_MECHANICS_LESSONS,
)
from physics_playground.subjects.mechanics.foundations_lesson import (
    ACTIVITIES,
    MEASUREMENT_EXAMPLE,
    MODELS_MEASUREMENTS_LESSON,
    OBJECTIVES,
)

LESSON_ID = "m01-measurement-models"


def _lesson_app(monkeypatch, tmp_path) -> AppTest:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    app = AppTest.from_file("app.py")
    app.query_params["simulation"] = "cannonball"
    app.query_params["lesson"] = LESSON_ID
    return app.run(timeout=30)


def _button_with_key(app: AppTest, suffix: str):
    return next(button for button in app.button if button.key and button.key.endswith(suffix))


def test_scientific_content_distinguishes_system_model_and_experiment() -> None:
    narrative = " ".join(section.narrative for section in MODELS_MEASUREMENTS_LESSON.sections)
    assert "physical system" in narrative
    assert "A simulation executes a model" in narrative
    assert "not automatically an experiment" in narrative
    assert "independent variable" in narrative and "dependent variable" in narrative
    assert "Changing controls without a prediction" in narrative
    assert "opening a lesson records no mastery" in narrative
    assert "scaled visual" in narrative and "schematic diagram" in narrative
    assert "uncertainty" in narrative and "accuracy" in narrative and "precision" in narrative


def test_worked_measurement_has_units_uncertainty_and_honest_precision() -> None:
    assert MEASUREMENT_EXAMPLE.final_answer == "v_avg ≈ (1.46 ± 0.06) m/s"
    assert "m/s" in MEASUREMENT_EXAMPLE.unit_check
    assert "systematic bias" in MEASUREMENT_EXAMPLE.final_interpretation
    raw_speed = 6.0 / 4.1
    assert round(raw_speed, 2) == 1.46
    assert all(
        value.display_value and "±" in value.display_value
        for value in MEASUREMENT_EXAMPLE.known_values
    )


def test_every_activity_and_checkpoint_connects_to_objective_evidence() -> None:
    objective_ids = {objective.id for objective in OBJECTIVES}
    components = [
        component
        for section in MODELS_MEASUREMENTS_LESSON.sections
        for component in section.components
    ]
    evidence_bearing = [
        component
        for component in components
        if isinstance(component, SimulationActivity | CheckpointQuestion)
    ]
    assert evidence_bearing
    assert all(
        component.objective_ids and set(component.objective_ids) <= objective_ids
        for component in evidence_bearing
    )
    observation_activities = [item for item in ACTIVITIES if item.evidence_prompt]
    assert {item.id for item in observation_activities} == {
        "m01-guided-observation",
        "m01-read-graph",
    }
    assert all(item.expected_reflection for item in observation_activities)


def test_lesson_meets_curriculum_specification_without_authoring_lesson_two() -> None:
    roadmap = next(item for item in INTRODUCTORY_MECHANICS_LESSONS if item.id == LESSON_ID)
    assert MODELS_MEASUREMENTS_LESSON.id == roadmap.id
    assert MODELS_MEASUREMENTS_LESSON.estimated_minutes == roadmap.estimated_minutes
    assert set(roadmap.core_concepts) <= {"SI units", "dimensions", "uncertainty", "models"}
    statements = " ".join(objective.statement.lower() for objective in OBJECTIVES)
    for concept in ("units", "precision", "physical system", "assumptions", "limitations"):
        assert concept in statements
    assert any(
        isinstance(item, WorkedExample)
        for section in MODELS_MEASUREMENTS_LESSON.sections
        for item in section.components
    )
    assert any(
        isinstance(item, MisconceptionCallout)
        for section in MODELS_MEASUREMENTS_LESSON.sections
        for item in section.components
    )
    assert MODELS_MEASUREMENTS_LESSON.next_lesson_id == "m02-position-velocity"
    assert MODELS_MEASUREMENTS_LESSON.next_lesson_title == (
        "Position, displacement, velocity, and speed"
    )


def test_observation_requires_reasoning_and_round_trips() -> None:
    progress = PathwayProgress(LESSON_ID)
    required = tuple(item.id for item in ACTIVITIES)
    updated = progress.save_activity_response(
        "m01-guided-observation",
        "I changed angle, held speed and gravity fixed, and recorded range in metres.",
        required_activity_ids=required,
        required_checkpoint_ids=(),
    )
    assert "m01-guided-observation" in updated.completed_activity_ids
    assert dict(updated.activity_responses)["m01-guided-observation"].startswith("I changed")
    restored = PathwayProgress.from_dict(updated.to_dict(), lesson_id=LESSON_ID)
    assert restored.activity_responses == updated.activity_responses
    assert not restored.mastered_objective_ids


def test_opening_and_running_do_not_create_mastery_or_evidence(monkeypatch, tmp_path) -> None:
    app = _lesson_app(monkeypatch, tmp_path)
    assert not app.exception
    assert any(
        header.value == "Guided lesson: Models, Measurements, and Representations"
        for header in app.header
    )
    progress = app.session_state[SHARED_STATE_KEYS.education_progress][LESSON_ID]
    assert not progress.mastered_objective_ids
    evidence_key = feature_key("education", "objective_evidence")
    assert evidence_key not in app.session_state or not app.session_state[evidence_key]

    next(button for button in app.button if button.label == "Begin lesson").click().run(timeout=30)
    assert any("Section 1 of 5" in heading.value for heading in app.subheader)
    assert evidence_key not in app.session_state or not app.session_state[evidence_key]


def test_guided_observation_records_a_reflection_not_objective_evidence(
    monkeypatch, tmp_path
) -> None:
    app = _lesson_app(monkeypatch, tmp_path)
    navigation = next(item for item in app.selectbox if item.label == "Lesson navigation")
    navigation.set_value("diagrams-and-observation").run(timeout=30)
    response = next(
        area
        for area in app.text_area
        if area.label == "Record your controlled observation and reasoning"
    )
    save = _button_with_key(app, "m01-guided-observation.complete")
    assert save.disabled
    response.set_value(
        "At fixed speed and gravity, increasing angle from 30° to 45° increased range; graph rounding limits the last digit."
    ).run(timeout=30)
    _button_with_key(app, "m01-guided-observation.complete").click().run(timeout=30)
    progress = app.session_state[SHARED_STATE_KEYS.education_progress][LESSON_ID]
    assert "m01-guided-observation" in progress.completed_activity_ids
    assert dict(progress.activity_responses)["m01-guided-observation"].startswith("At fixed speed")
    # An ungraded observation is never recorded as objective evidence or mastery.
    evidence_key = feature_key("education", "objective_evidence")
    assert evidence_key not in app.session_state or not app.session_state[evidence_key]
    assert not progress.mastered_objective_ids
