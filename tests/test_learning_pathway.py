"""Sequencing, completion, reset, and restoration tests for the first pathway."""

from __future__ import annotations

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    configure_application_callbacks,
    reset_application_callbacks,
)
from physics_playground.education.models import (
    ActivityPhase,
    CheckpointQuestion,
    EducationEventKind,
)
from physics_playground.education.progress import PathwayProgress
from physics_playground.notebook import ExperimentNotebook
from physics_playground.presentation import pathway_ui, profile_ui
from physics_playground.profiles import LocalProfile, ProfileStore
from physics_playground.state_keys import SHARED_STATE_KEYS, simulation_key
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON


def _requirements() -> tuple[tuple[str, ...], tuple[str, ...]]:
    activities = tuple(item.id for item in CANNONBALL_LESSON.activity_sequence)
    checkpoints = tuple(
        component.id
        for section in CANNONBALL_LESSON.sections
        for component in section.components
        if isinstance(component, CheckpointQuestion)
    )
    return activities, checkpoints


def test_pathway_contains_the_complete_required_sequence() -> None:
    assert tuple(item.phase for item in CANNONBALL_LESSON.activity_sequence) == tuple(ActivityPhase)
    assert CANNONBALL_LESSON.sections[0].narrative.startswith("A projectile")
    assert (
        CANNONBALL_LESSON.next_lesson_title == "Cumulative check: models through projectile motion"
    )
    assert "cannonball" in CANNONBALL_LESSON.simulation_ids


def test_completion_requires_every_activity_and_checkpoint() -> None:
    activities, checkpoints = _requirements()
    progress = PathwayProgress(CANNONBALL_LESSON.id)
    progress = progress.save_prediction(
        "45 degrees balances horizontal speed and time aloft.",
        activities[0],
        required_activity_ids=activities,
        required_checkpoint_ids=checkpoints,
    )
    for activity_id in activities[1:-1]:
        progress = progress.complete_activity(
            activity_id,
            required_activity_ids=activities,
            required_checkpoint_ids=checkpoints,
        )
    for checkpoint_id in checkpoints:
        progress = progress.complete_checkpoint(
            checkpoint_id,
            required_activity_ids=activities,
            required_checkpoint_ids=checkpoints,
        )
    assert not progress.completed
    progress = progress.save_reflection(
        "The graph showed why complementary paths can share a range.",
        activities[-1],
        required_activity_ids=activities,
        required_checkpoint_ids=checkpoints,
    )
    assert progress.completed


def test_returning_learner_restores_prediction_without_repeating_and_can_reset() -> None:
    activities, checkpoints = _requirements()
    saved = PathwayProgress(CANNONBALL_LESSON.id).save_prediction(
        "I predict 45 degrees.",
        activities[0],
        required_activity_ids=activities,
        required_checkpoint_ids=checkpoints,
    )
    restored = PathwayProgress.from_dict(saved.to_dict(), lesson_id=CANNONBALL_LESSON.id)
    assert restored.prediction == "I predict 45 degrees."
    assert activities[0] in restored.completed_activity_ids
    reset = restored.reset_prediction(activities[0])
    assert reset.prediction is None
    assert activities[0] not in reset.completed_activity_ids
    assert not reset.completed


def test_completion_event_uses_existing_application_callback_seam(monkeypatch) -> None:
    activities, checkpoints = _requirements()
    complete = PathwayProgress(
        CANNONBALL_LESSON.id,
        completed_activity_ids=activities,
        completed_checkpoint_ids=checkpoints,
        prediction="45 degrees",
        reflection="The graph connected range to sin two theta.",
        completed=True,
    )
    events = []
    configure_application_callbacks(ApplicationCallbacks(on_event=events.append))
    state = {SHARED_STATE_KEYS.profiles_active_id: "learner-1"}
    monkeypatch.setattr(pathway_ui.st, "session_state", state)
    try:
        pathway_ui._save_progress(
            complete,
            kind=EducationEventKind.ACTIVITY_COMPLETED,
            activity_id=activities[-1],
        )
    finally:
        reset_application_callbacks()
    assert events[0].kind is EducationEventKind.LESSON_COMPLETED
    assert events[0].completed is True
    assert state[SHARED_STATE_KEYS.education_progress][CANNONBALL_LESSON.id] == complete


def test_completion_event_persists_through_profile_subscriber(monkeypatch, tmp_path) -> None:
    activities, checkpoints = _requirements()
    complete = PathwayProgress(
        CANNONBALL_LESSON.id,
        completed_activity_ids=activities,
        completed_checkpoint_ids=checkpoints,
        prediction="45 degrees",
        reflection="The graph connected the equation to the measured range.",
        completed=True,
    )
    store = ProfileStore(tmp_path / "profiles.sqlite3")
    profile = LocalProfile("learner-1", "Ada")
    store.save(profile)
    state = {
        SHARED_STATE_KEYS.profiles_store: store,
        SHARED_STATE_KEYS.profiles_active_id: profile.id,
        SHARED_STATE_KEYS.education_progress: {},
        SHARED_STATE_KEYS.notebook: ExperimentNotebook(),
    }
    monkeypatch.setattr(pathway_ui.st, "session_state", state)
    configure_application_callbacks(
        ApplicationCallbacks(on_event=profile_ui.persist_application_event)
    )
    try:
        pathway_ui._save_progress(
            complete,
            kind=EducationEventKind.ACTIVITY_COMPLETED,
            activity_id=activities[-1],
        )
    finally:
        reset_application_callbacks()
    restored = store.load(profile.id)
    assert restored.educational_progress[CANNONBALL_LESSON.id]["completed"] is True


def test_profile_store_round_trips_pathway_progress(tmp_path) -> None:
    activities, checkpoints = _requirements()
    progress = PathwayProgress(
        CANNONBALL_LESSON.id,
        completed_activity_ids=(activities[0],),
        prediction="45 degrees",
    )
    profile = LocalProfile(
        "learner-1",
        "Ada",
        educational_progress={CANNONBALL_LESSON.id: progress.to_dict()},
    )
    store = ProfileStore(tmp_path / "profiles.sqlite3")
    store.save(profile)
    restored = store.load(profile.id)
    assert restored.educational_progress[CANNONBALL_LESSON.id]["prediction"] == "45 degrees"
    assert checkpoints


def test_loading_profile_restores_typed_pathway_progress(monkeypatch) -> None:
    activity_id = CANNONBALL_LESSON.activity_sequence[0].id
    progress = PathwayProgress(
        CANNONBALL_LESSON.id,
        completed_activity_ids=(activity_id,),
        prediction="45 degrees",
    )
    profile = LocalProfile(
        "learner-1",
        "Ada",
        educational_progress={CANNONBALL_LESSON.id: progress.to_dict()},
    )
    state = {}
    monkeypatch.setattr(profile_ui.st, "session_state", state)
    profile_ui.load_into_session(profile)
    restored = state[SHARED_STATE_KEYS.education_progress][CANNONBALL_LESSON.id]
    assert isinstance(restored, PathwayProgress)
    assert restored.prediction == "45 degrees"


def test_notebook_reflection_is_restorable_and_replaces_prior_response() -> None:
    notebook = ExperimentNotebook()
    first = notebook.save_lesson_reflection(
        lesson_id=CANNONBALL_LESSON.id,
        prompt="What did the graph reveal?",
        response="Complementary angles matched.",
    )
    second = notebook.save_lesson_reflection(
        lesson_id=CANNONBALL_LESSON.id,
        prompt="What did the graph reveal?",
        response="The range curve followed sin(2 theta).",
    )
    assert first.id != second.id
    assert len(notebook.lesson_reflections) == 1
    restored = ExperimentNotebook.from_dict(
        {
            "trials": [],
            "lesson_reflections": [
                {
                    "id": second.id,
                    "lesson_id": second.lesson_id,
                    "timestamp": second.timestamp,
                    "prompt": second.prompt,
                    "response": second.response,
                }
            ],
        }
    )
    assert restored.lesson_reflections == [second]


def test_pathway_mode_links_do_not_remove_direct_mode_state() -> None:
    for activity in CANNONBALL_LESSON.activity_sequence:
        if activity.mode is not None:
            key = simulation_key(activity.simulation_id, "learning_mode")
            assert key == "physics_studio.simulation.cannonball.learning_mode"
    assert {item.mode.value for item in CANNONBALL_LESSON.activity_sequence if item.mode} == {
        "Explore",
        "Compare",
        "Analyze",
        "Model",
    }
