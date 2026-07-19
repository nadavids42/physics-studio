from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from physics_playground.notebook import ExperimentNotebook
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, simulation_key
from physics_playground.subjects.mechanics.cannonball.interactions import target_for_seed
from physics_playground.subjects.mechanics.cannonball.physics import ProjectileParameters
from physics_playground.units import EARTH_GRAVITY_M_S2


def _cannon_app(monkeypatch: pytest.MonkeyPatch, tmp_path) -> AppTest:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    app = AppTest.from_file("app.py")
    app.query_params["simulation"] = "cannonball"
    app.session_state[simulation_key("cannonball", "quiz_revealed")] = True
    app.session_state[simulation_key("cannonball", "quiz_guess")] = "45°"
    return app


def test_target_generation_is_deterministic_and_seed_sensitive() -> None:
    assert target_for_seed(20260710) == target_for_seed(20260710)
    assert target_for_seed(20260710) != target_for_seed(20260711)


def test_lesson_activity_selects_runtime_mode(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    app = _cannon_app(monkeypatch, tmp_path)
    app.query_params["lesson"] = "projectile-motion-from-components"
    app.session_state[feature_key("education", "projectile-motion-from-components.section")] = (
        "worked-example"
    )
    app.run(timeout=30)
    next(button for button in app.button if button.label == "Open Analyze mode").click().run(
        timeout=30
    )

    assert not app.exception
    assert app.session_state[simulation_key("cannonball", "learning_mode")] == "Analyze"
    linked = [
        iframe
        for iframe in app.get("iframe")
        if "Linked projectile representations" in iframe.proto.srcdoc
    ]
    assert len(linked) == 1


def test_notebook_replay_restores_target_controls_and_setup(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    parameters = ProjectileParameters(32.0, 37.0, EARTH_GRAVITY_M_S2)
    notebook = ExperimentNotebook()
    notebook.add_trial(
        simulation_id="cannonball",
        parameters={**parameters.to_dict(), "target_m": 44.4},
        prediction="45°",
        result_summary="Saved launch",
        metrics={"range_m": 50.0},
        earned_badges=(),
        random_seed=20260710,
        model_version="projectile-2.0",
    )
    app = _cannon_app(monkeypatch, tmp_path)
    app.session_state[SHARED_STATE_KEYS.notebook] = notebook
    app.run(timeout=30)
    next(button for button in app.button if button.label == "↩ Reuse setup").click().run(timeout=30)

    assert not app.exception
    assert next(item for item in app.slider if item.label == "Launch speed (m/s)").value == 32.0
    assert next(item for item in app.slider if item.label == "Launch angle (degrees)").value == 37
    assert any("Target: 44.4 m" in item.value for item in app.info)
    assert SHARED_STATE_KEYS.notebook_setup_request not in app.session_state
