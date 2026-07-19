from __future__ import annotations

from streamlit.testing.v1 import AppTest

from physics_playground.education.assessments import (
    AssessmentAttempt,
    ObjectiveEvidenceRecord,
)
from physics_playground.education.progress import PathwayProgress
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, simulation_key

LESSON_ID = "projectile-motion-from-components"


def lesson_app(monkeypatch, tmp_path) -> AppTest:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    app = AppTest.from_file("app.py")
    app.query_params["simulation"] = "cannonball"
    app.query_params["lesson"] = LESSON_ID
    return app.run(timeout=30)


def button_with_key(app: AppTest, suffix: str):
    return next(button for button in app.button if button.key and button.key.endswith(suffix))


def test_cannonball_guided_lesson_full_sequence_and_resume(monkeypatch, tmp_path) -> None:
    app = lesson_app(monkeypatch, tmp_path)
    assert not app.exception
    assert any(
        header.value == "Guided lesson: Projectile motion from components" for header in app.header
    )
    assert any(subheader.value == "Orientation" for subheader in app.subheader)
    assert any(radio.label == "Learning mode" for radio in app.radio)
    assert any(selectbox.label == "Lesson navigation" for selectbox in app.selectbox)

    next(button for button in app.button if button.label == "Begin lesson").click().run(timeout=30)
    assert any("Section 1 of 4" in heading.value for heading in app.subheader)
    assert any("Figure: Launch velocity components" in item.value for item in app.markdown)

    prediction = next(
        area for area in app.text_area if area.label == "Record your prediction and physical reason"
    )
    prediction.set_value("45 degrees balances horizontal speed and time aloft.")
    button_with_key(app, f"{LESSON_ID}.save_prediction").click().run(timeout=30)
    next(button for button in app.button if button.label == "Continue to next section").click().run(
        timeout=30
    )

    button_with_key(app, "explore-components.complete").click().run(timeout=30)
    button_with_key(app, "compare-complements.complete").click().run(timeout=30)
    next(button for button in app.button if button.label == "Continue to next section").click().run(
        timeout=30
    )

    answer = next(radio for radio in app.radio if radio.label == "Choose an answer")
    answer.set_value("angle-60").run(timeout=30)
    next(radio for radio in app.radio if radio.label == "Learning mode").set_value("Compare").run(
        timeout=30
    )
    assert (
        next(radio for radio in app.radio if radio.label == "Choose an answer").value == "angle-60"
    )
    assert not any(
        "Complementary angles have equal sin(2theta)" in item.value for item in app.success
    )
    button_with_key(app, "range-checkpoint.submit").click().run(timeout=30)
    button_with_key(app, "analyze-range.complete").click().run(timeout=30)
    next(button for button in app.button if button.label == "Continue to next section").click().run(
        timeout=30
    )

    button_with_key(app, "model-drag.complete").click().run(timeout=30)
    reflection = next(area for area in app.text_area if area.label == "Notebook reflection")
    reflection.set_value("The ideal equation explains symmetry; drag breaks that symmetry.")
    button_with_key(app, f"{LESSON_ID}.save_reflection").click().run(timeout=30)
    next(button for button in app.button if button.label == "Complete lesson").click().run(
        timeout=30
    )

    progress = app.session_state[SHARED_STATE_KEYS.education_progress][LESSON_ID]
    assert isinstance(progress, PathwayProgress)
    assert progress.completed
    assert len(progress.completed_section_ids) == 4
    assert any(subheader.value == "Recommended next step" for subheader in app.subheader)
    attempts = app.session_state[feature_key("education", "assessment_attempts")]
    evidence = app.session_state[feature_key("education", "objective_evidence")]
    assert all(isinstance(item, AssessmentAttempt) for item in attempts)
    assert all(isinstance(item, ObjectiveEvidenceRecord) for item in evidence)
    assert progress.assessment_attempt_ids and attempts[0].id in progress.assessment_attempt_ids

    resumed = app.run(timeout=30)
    navigation = next(
        selectbox for selectbox in resumed.selectbox if selectbox.label == "Lesson navigation"
    )
    assert navigation.value == "validation-and-limits"


def test_lesson_and_simulation_navigation_use_distinct_state(monkeypatch, tmp_path) -> None:
    app = lesson_app(monkeypatch, tmp_path)
    next(button for button in app.button if button.label == "Begin lesson").click().run(timeout=30)
    lesson_key = feature_key("education", f"{LESSON_ID}.section")
    mode_key = simulation_key("cannonball", "learning_mode")
    assert lesson_key != mode_key
    assert app.session_state[lesson_key] == "system-and-prediction"
    assert app.session_state[mode_key] == "Explore"
