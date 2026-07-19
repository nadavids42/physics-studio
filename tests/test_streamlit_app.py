"""High-value Streamlit application navigation and rendering tests."""

import pytest
from streamlit.testing.v1 import AppTest

from physics_playground.accessibility_settings import AccessibilitySettings
from physics_playground.education.progress import PathwayProgress
from physics_playground.state_keys import SHARED_STATE_KEYS, simulation_key
from physics_playground.subjects.mechanics.foundations_lesson import MODELS_MEASUREMENTS_LESSON
from physics_playground.subjects.mechanics.two_d_motion_lesson import TWO_D_MOTION_LESSON

LESSON_ID = "projectile-motion-from-components"


def _app(monkeypatch, tmp_path) -> AppTest:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    return AppTest.from_file("app.py")


def test_home_is_primary_discovery_and_sidebar_is_hierarchical(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path).run(timeout=30)

    assert not app.exception
    assert not app.radio
    assert any(title.value == "Physics Studio" for title in app.title)
    labels = {selectbox.label for selectbox in app.selectbox}
    assert {"Browse by subject", "Unit or collection", "Concept"} <= labels
    subject_selector = next(item for item in app.selectbox if item.label == "Browse by subject")
    assert subject_selector.options == [
        "All subjects",
        "Mechanics",
        "Waves and oscillations",
        "Light and electricity",
        "Fluids and matter",
    ]
    assert "Cannonball Launcher — Projectile Motion" not in subject_selector.options
    assert any(item.label == "Search lessons and simulations" for item in app.text_input)
    assert any(button.label == "Open recommended lesson" for button in app.button)


def test_recommendation_opens_lesson_without_gating_simulations(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path).run(timeout=30)
    recommendation = next(
        button for button in app.button if button.label == "Open recommended lesson"
    )
    recommendation.click().run(timeout=30)

    assert not app.exception
    assert any(header.value == "Cannonball Launcher — Projectile Motion" for header in app.header)
    assert any(button.label == "Begin lesson" for button in app.button)
    assert app.query_params["simulation"] == ["cannonball"]
    assert app.query_params["lesson"] == [MODELS_MEASUREMENTS_LESSON.id]
    assert any(button.label == "← Back to discovery" for button in app.button)


def test_stable_query_identifiers_open_simulation_and_lesson(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.query_params["lesson"] = LESSON_ID
    app.session_state[SHARED_STATE_KEYS.education_progress] = {
        "m05-constant-acceleration": PathwayProgress("m05-constant-acceleration", completed=True),
        TWO_D_MOTION_LESSON.id: PathwayProgress(TWO_D_MOTION_LESSON.id, completed=True),
    }
    app.run(timeout=30)

    assert not app.exception
    assert any(header.value == "Cannonball Launcher — Projectile Motion" for header in app.header)
    assert any(header.value.startswith("Guided lesson:") for header in app.header)
    assert any(selectbox.label == "Lesson navigation" for selectbox in app.selectbox)


def test_incomplete_prerequisites_block_the_lesson_pathway_not_the_simulation(
    monkeypatch, tmp_path
) -> None:
    """A learner who jumps straight to projectile motion sees a locked pathway,
    but the underlying Cannonball simulation itself stays reachable."""

    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.query_params["lesson"] = LESSON_ID
    app.run(timeout=30)

    assert not app.exception
    assert any(header.value == "Cannonball Launcher — Projectile Motion" for header in app.header)
    assert any(header.value.startswith("Guided lesson:") for header in app.header)
    assert not any(selectbox.label == "Lesson navigation" for selectbox in app.selectbox)
    assert any("unlocks after you complete" in warning.value for warning in app.warning)
    assert any(
        button.label == "Open 2D motion: combining independent components" for button in app.button
    )
    assert any(radio.label == "Learning mode" for radio in app.radio)


@pytest.mark.parametrize(
    "simulation_id",
    ("cannonball", "pendulum", "thin_lenses", "buoyancy"),
)
def test_representative_subject_pages_smoke_without_errors(
    monkeypatch, tmp_path, simulation_id
) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = simulation_id
    app.run(timeout=30)

    assert not app.exception
    assert app.query_params["simulation"] == [simulation_id]
    assert any(button.label == "← Back to discovery" for button in app.button)


def test_cannonball_setup_applies_and_notes_do_not_rerun_player(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.session_state[simulation_key("cannonball", "quiz_revealed")] = True
    app.session_state[simulation_key("cannonball", "quiz_guess")] = "45°"
    app.session_state[simulation_key("cannonball", "speed")] = 31.0
    app.run(timeout=30)

    assert any(button.label == "Apply launch setup" for button in app.button)
    speed = next(item for item in app.slider if item.label == "Launch speed (m/s)")
    assert speed.value == 31.0
    original_setup_document = app.get("iframe")[0].proto.srcdoc
    speed.set_value(33.0)
    next(button for button in app.button if button.label == "Apply launch setup").click().run(
        timeout=30
    )
    assert app.session_state[simulation_key("cannonball", "speed")] == 33.0
    assert app.get("iframe")[0].proto.srcdoc != original_setup_document
    iframe_before = app.get("iframe")[0].proto.srcdoc
    observation = next(
        item for item in app.text_input if item.label == "Optional notebook observation"
    )
    observation.set_value("The range stayed fixed.").run(timeout=30)

    assert not app.exception
    assert app.get("iframe")[0].proto.srcdoc == iframe_before
    assert app.session_state[simulation_key("cannonball", "observation")] == (
        "The range stayed fixed."
    )


def test_standalone_cannonball_keeps_direct_mode_access(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.session_state[simulation_key("cannonball", "quiz_revealed")] = True
    app.session_state[simulation_key("cannonball", "quiz_guess")] = "45°"
    app.run(timeout=30)

    assert any(button.label == "Start guided lesson" for button in app.button)
    assert any(radio.label == "Learning mode" for radio in app.radio)
    assert not any(selectbox.label == "Lesson navigation" for selectbox in app.selectbox)


@pytest.mark.parametrize(
    "mode",
    ["Compare", "Analyze"],
)
def test_cannonball_interactive_chart_examples_render_in_page(monkeypatch, tmp_path, mode) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.session_state[simulation_key("cannonball", "quiz_revealed")] = True
    app.session_state[simulation_key("cannonball", "quiz_guess")] = "45°"
    app.session_state[simulation_key("cannonball", "learning_mode")] = mode
    app.run(timeout=30)

    assert not app.exception
    linked = [
        iframe
        for iframe in app.get("iframe")
        if "Linked projectile representations" in iframe.proto.srcdoc
    ]
    assert len(linked) == 1
    assert linked[0].proto.srcdoc.count('class="linked-graph"') == 3


def test_accessibility_preferences_apply_without_hiding_controls(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path).run(timeout=30)
    for label in (
        "Reduce animation and disable autoplay",
        "High-contrast display",
        "Larger interface text",
    ):
        next(item for item in app.checkbox if item.label == label).set_value(True)
    app.run(timeout=30)

    assert not app.exception
    assert app.session_state[SHARED_STATE_KEYS.accessibility_settings] == AccessibilitySettings(
        reduced_motion=True,
        high_contrast=True,
        large_text=True,
    )
    assert any(button.label == "Home and discovery" for button in app.button)


def test_model_limit_error_has_actionable_message(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.session_state[simulation_key("cannonball", "quiz_revealed")] = True
    app.session_state[simulation_key("cannonball", "quiz_guess")] = "45°"
    app.session_state[simulation_key("cannonball", "learning_mode")] = "Model"
    app.run(timeout=30)
    next(item for item in app.number_input if item.label == "Model speed").set_value(100.0)
    next(item for item in app.number_input if item.label == "Model angle").set_value(89.0)
    next(item for item in app.number_input if item.label == "Maximum time (s)").set_value(1.0)
    app.run(timeout=30)

    assert not app.exception
    assert any("did not land" in error.value for error in app.error)
    assert any("Increase the limit" in error.value for error in app.error)
