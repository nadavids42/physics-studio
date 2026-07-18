import pytest

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    BadgeEarned,
    ProgressChanged,
    configure_application_callbacks,
    publish,
    reset_application_callbacks,
)
from physics_playground.contracts import MissionEvaluation
from physics_playground.missions.service import MissionProgress, evaluate_run
from physics_playground.presentation import profile_ui
from physics_playground.state_keys import SHARED_STATE_KEYS


@pytest.fixture(autouse=True)
def reset_callbacks_after_test():
    reset_application_callbacks()
    yield
    reset_application_callbacks()


def test_mission_evaluation_delivers_typed_events_in_order() -> None:
    events = []
    progress = MissionProgress(pending_explanations={"collision_predict"})
    earned = evaluate_run(progress, "bumper_cars", (), events.append)
    assert earned == ("collision_predict",)
    assert events == [
        BadgeEarned("bumper_cars", "collision_predict"),
        ProgressChanged("bumper_cars", ("collision_predict",)),
    ]


def test_mission_evaluation_publishes_nothing_without_a_change() -> None:
    events = []
    progress = MissionProgress(completed={"collision_predict"})
    evaluate_run(
        progress,
        "bumper_cars",
        (MissionEvaluation("collision_swap", False, "not yet"),),
        events.append,
    )
    assert events == []


def test_application_callback_delivery_is_synchronous() -> None:
    events = []
    configure_application_callbacks(ApplicationCallbacks(on_event=events.append))
    event = BadgeEarned("pendulum", "pend_predict")
    publish(event)
    assert events == [event]


def test_application_callback_failure_is_not_suppressed() -> None:
    expected = RuntimeError("persistence failed")

    def fail(_event):
        raise expected

    configure_application_callbacks(ApplicationCallbacks(on_event=fail))
    with pytest.raises(RuntimeError, match="persistence failed") as caught:
        publish(BadgeEarned("pendulum", "pend_predict"))
    assert caught.value is expected


def test_persistence_failure_is_recorded_and_logged(monkeypatch, caplog) -> None:
    class FailingStore:
        def save(self, _profile):
            raise AssertionError("load should fail first")

        def load(self, _profile_id):
            raise OSError("disk unavailable")

    state = {
        SHARED_STATE_KEYS.profiles_store: FailingStore(),
        SHARED_STATE_KEYS.profiles_active_id: "ada",
    }
    monkeypatch.setattr(profile_ui.st, "session_state", state)
    assert profile_ui.persist_active_session() is False
    assert state[SHARED_STATE_KEYS.profiles_persistence_error] == "disk unavailable"
    assert "Could not persist the active profile" in caplog.text
