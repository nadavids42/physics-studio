"""High-value Streamlit application navigation and rendering tests."""

from streamlit.testing.v1 import AppTest

from physics_playground.state_keys import simulation_key

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
    assert any(button.label == "Submit prediction" for button in app.button)
    assert app.query_params["simulation"] == ["cannonball"]
    assert app.query_params["lesson"] == [LESSON_ID]
    assert any(button.label == "← Back to discovery" for button in app.button)


def test_stable_query_identifiers_open_simulation_and_lesson(monkeypatch, tmp_path) -> None:
    app = _app(monkeypatch, tmp_path)
    app.query_params["simulation"] = "cannonball"
    app.query_params["lesson"] = LESSON_ID
    app.run(timeout=30)

    assert not app.exception
    assert any(header.value == "Cannonball Launcher — Projectile Motion" for header in app.header)
    assert any(
        expander.label == "Learning pathway: Projectile motion from components"
        for expander in app.expander
    )


def test_cannonball_setup_is_committed_and_notes_do_not_rerun_player(monkeypatch, tmp_path) -> None:
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
