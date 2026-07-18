"""Tests for trial storage, comparison, deletion, reset, and export."""

import csv
import json
from io import StringIO

from physics_playground.notebook import ExperimentNotebook


def add_example(notebook: ExperimentNotebook, speed: float, *, label: str = "Run"):
    return notebook.add_trial(
        simulation_id="bumper_cars",
        parameters={"mass_a_kg": 2.0, "velocity_a_m_s": speed},
        prediction="They swap",
        result_summary=f"Car A started at {speed} m/s",
        metrics={"velocity_a_after_m_s": 0.0, "energy_lost_j": speed},
        earned_badges=("collision_swap",),
        random_seed=42,
        model_version="collision-1.0",
        learner_observation="The cars exchanged motion.",
        label=label,
    )


def test_trials_receive_monotonic_numbers_and_required_fields() -> None:
    notebook = ExperimentNotebook()
    first = add_example(notebook, 4.0)
    second = add_example(notebook, 6.0)
    assert (first.trial_number, second.trial_number) == (1, 2)
    assert first.timestamp
    assert first.prediction == "They swap"
    assert first.earned_badges == ("collision_swap",)
    assert first.random_seed == 42


def test_filter_pin_delete_and_reset() -> None:
    notebook = ExperimentNotebook()
    bumper = add_example(notebook, 4.0)
    notebook.add_trial(
        simulation_id="pendulum",
        parameters={"length_m": 2.0},
        prediction=None,
        result_summary="Swing",
        metrics={"period_s": 2.8},
        earned_badges=(),
        random_seed=7,
        model_version="pendulum-legacy",
    )
    assert notebook.filtered("bumper_cars") == [bumper]
    notebook.pin(bumper.id)
    assert notebook.pinned_run_a_id == bumper.id
    notebook.delete(bumper.id)
    assert notebook.pinned_run_a_id is None
    notebook.reset()
    assert notebook.trials == []
    assert notebook.next_trial_number == 1


def test_trial_comparison_reports_metric_and_parameter_changes() -> None:
    notebook = ExperimentNotebook()
    run_a = add_example(notebook, 4.0, label="Run A")
    run_b = add_example(notebook, 6.0, label="Run B")
    comparison = notebook.compare(run_a.id, run_b.id)
    assert comparison.metric_deltas["energy_lost_j"] == 2.0
    assert comparison.changed_parameters["velocity_a_m_s"] == (4.0, 6.0)


def test_json_export_contains_structured_trial() -> None:
    notebook = ExperimentNotebook()
    add_example(notebook, 4.0)
    payload = json.loads(notebook.to_json())
    assert payload["trials"][0]["simulation_id"] == "bumper_cars"
    assert payload["trials"][0]["learner_observation"] == "The cars exchanged motion."


def test_csv_export_flattens_parameters_and_metrics() -> None:
    notebook = ExperimentNotebook()
    add_example(notebook, 4.0)
    rows = list(csv.DictReader(StringIO(notebook.to_csv())))
    assert rows[0]["parameter.velocity_a_m_s"] == "4.0"
    assert rows[0]["metric.energy_lost_j"] == "4.0"
    assert rows[0]["earned_badges"] == "collision_swap"
