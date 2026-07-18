from physics_playground.setup_handoff import (
    SimulationSetupRequest,
    consume_setup_request,
    queue_setup_request,
)
from physics_playground.state_keys import SHARED_STATE_KEYS


def test_setup_request_round_trip() -> None:
    state = {}
    request = SimulationSetupRequest(
        simulation_id="cannonball",
        parameters={"launch_speed_m_s": 20.0, "launch_angle_deg": 35.0},
        source_label="Worked example",
        preset_id="projectile-no-drag",
    )
    queue_setup_request(state, request)
    assert state[SHARED_STATE_KEYS.notebook_setup_request]["simulation_id"] == "cannonball"
    assert consume_setup_request(state, "cannonball") == request
    assert SHARED_STATE_KEYS.notebook_setup_request not in state


def test_setup_request_is_left_for_its_target_simulation() -> None:
    state = {}
    request = SimulationSetupRequest("cannonball", {"launch_speed_m_s": 20.0}, "Notebook")
    queue_setup_request(state, request)
    assert consume_setup_request(state, "pendulum") is None
    assert SHARED_STATE_KEYS.notebook_setup_request in state
