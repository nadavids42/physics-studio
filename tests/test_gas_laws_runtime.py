from __future__ import annotations

from contextlib import nullcontext
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from physics_playground.missions.service import MissionProgress
from physics_playground.notebook import ExperimentNotebook
from physics_playground.presentation.learning_modes import run_model_safely
from physics_playground.state_keys import SHARED_STATE_KEYS, simulation_key
from physics_playground.subjects.fluids_and_matter.gas_laws.physics import (
    GasLawParameters,
    simulate,
)


def _gas_app(monkeypatch: pytest.MonkeyPatch, tmp_path, mode: str = "Explore") -> AppTest:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    app = AppTest.from_file("app.py")
    app.query_params["simulation"] = "gas_laws"
    app.session_state[simulation_key("gas_laws", "gas_quiz_revealed")] = True
    app.session_state[simulation_key("gas_laws", "gas_quiz_guess")] = "It doubles"
    app.session_state[simulation_key("gas_laws", "gas_mode")] = mode
    return app


@pytest.mark.parametrize(
    ("mode", "heading"),
    (
        ("Explore", "Explore: Constrain a gas process"),
        ("Compare", "Compare: Compression versus heating"),
        ("Analyze", "Analyze: P–V, V–T, and P–T relationships"),
        ("Model", "Model: One equation, three constrained laws"),
    ),
)
def test_gas_laws_runtime_preserves_all_four_modes(
    monkeypatch: pytest.MonkeyPatch, tmp_path, mode: str, heading: str
) -> None:
    app = _gas_app(monkeypatch, tmp_path, mode).run(timeout=30)

    assert not app.exception
    assert any(item.value == heading for item in app.subheader)


def test_explore_records_notebook_and_processes_missions(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    app = _gas_app(monkeypatch, tmp_path).run(timeout=30)
    scenario = next(item for item in app.selectbox if item.label == "Gas-law scenario")
    scenario.select("Boyle's law")
    next(button for button in app.button if button.label == "🎈 Run gas experiment").click().run(
        timeout=30
    )

    notebook = app.session_state[SHARED_STATE_KEYS.notebook]
    progress = app.session_state[SHARED_STATE_KEYS.missions_progress]
    assert isinstance(notebook, ExperimentNotebook)
    assert isinstance(progress, MissionProgress)
    assert len(notebook.trials) == 1
    assert notebook.trials[0].simulation_id == "gas_laws"
    assert notebook.trials[0].model_version == "gas-laws-1.0"
    assert {"gas_predict", "gas_boyle"} <= progress.completed


def test_invalid_parameters_use_standard_error_presentation() -> None:
    with (
        patch("streamlit.error") as error,
        patch("streamlit.expander", return_value=nullcontext()),
        patch("streamlit.code"),
    ):
        result = run_model_safely(lambda: simulate(GasLawParameters(amount_mol=0.0)))

    assert result is None
    error.assert_called_once()
    assert "could not finish safely" in error.call_args.args[0]


def test_result_is_stable_across_unrelated_rerun(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    app = _gas_app(monkeypatch, tmp_path).run(timeout=30)
    amount = next(item for item in app.slider if item.label == "Amount (mol)")
    amount.set_value(1.5)
    next(button for button in app.button if button.label == "🎈 Run gas experiment").click().run(
        timeout=30
    )

    notebook = app.session_state[SHARED_STATE_KEYS.notebook]
    iframe_before = app.get("iframe")[0].proto.srcdoc
    observation = next(
        item for item in app.text_input if item.label == "Optional notebook observation"
    )
    observation.set_value("Unrelated note edit").run(timeout=30)

    assert next(item for item in app.slider if item.label == "Amount (mol)").value == 1.5
    assert len(notebook.trials) == 1
    assert app.get("iframe")[0].proto.srcdoc == iframe_before
