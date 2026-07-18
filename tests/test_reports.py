import csv
import json
from io import StringIO

from physics_playground.notebook import ExperimentNotebook
from physics_playground.reports import build_report, generate_report_bundle


def notebook_with_trials():
    n = ExperimentNotebook()
    a = n.add_trial(
        simulation_id="bumper_cars",
        parameters={"mass_a_kg": 2.0, "restitution": 1.0},
        prediction="They swap",
        result_summary="Cars exchanged velocities",
        metrics={"momentum_after": 8.0, "energy_lost": 0.0},
        earned_badges=("collision_swap",),
        random_seed=1,
        model_version="collision-1.0",
        learner_observation="Momentum stayed constant.",
    )
    b = n.add_trial(
        simulation_id="bumper_cars",
        parameters={"mass_a_kg": 2.0, "restitution": 0.0},
        prediction="They stick",
        result_summary="Cars stuck together",
        metrics={"momentum_after": 8.0, "energy_lost": 8.0},
        earned_badges=("collision_stop",),
        random_seed=2,
        model_version="collision-1.0",
        learner_observation="Energy decreased.",
    )
    return n, a, b


def test_report_contains_required_sections_and_comparison():
    n, a, b = notebook_with_trials()
    report = build_report(n, [a.id, b.id], "Ada")
    assert report.scientist_name == "Ada" and report.question and report.assumptions
    assert report.changed_parameters["restitution"] == (1.0, 0.0)
    assert report.measurement_deltas["energy_lost"] == 8.0


def test_all_export_formats():
    n, a, b = notebook_with_trials()
    bundle = generate_report_bundle(n, [a.id, b.id], "Ada")
    assert "window.print" in bundle.html and "Cars exchanged velocities" in bundle.html
    assert "# Lab Report" in bundle.markdown and "Conclusion prompt" in bundle.markdown
    rows = list(csv.DictReader(StringIO(bundle.csv)))
    assert len(rows) == 2 and rows[0]["scientist"] == "Ada"
    payload = json.loads(bundle.json)
    assert payload["simulation_title"] == "Bumper Cars" and len(payload["trials"]) == 2


def test_mixed_simulation_report_is_rejected():
    n, a, _ = notebook_with_trials()
    other = n.add_trial(
        simulation_id="pendulum",
        parameters={},
        prediction=None,
        result_summary="swing",
        metrics={},
        earned_badges=(),
        random_seed=3,
        model_version="pendulum-2.0",
    )
    import pytest

    with pytest.raises(ValueError):
        build_report(n, [a.id, other.id], "Ada")
