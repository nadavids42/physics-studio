"""Version and invariant tests for the incremental frontend protocol."""

from copy import deepcopy

import pytest

from physics_playground.frontend_protocol import (
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    linked_projectile_envelope,
    validate_frontend_envelope,
)
from physics_playground.subjects.mechanics.cannonball.linked_representations import (
    linked_projectile_payload,
)
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_no_drag,
)


def _envelope():
    result = simulate_no_drag(ProjectileParameters(samples=24))
    payload = linked_projectile_payload((("Run A", result),))
    return linked_projectile_envelope(
        simulation_id=result.simulation_id,
        model_version=result.model_version,
        payload=payload,
    )


def test_v1_envelope_identifies_model_and_representation() -> None:
    envelope = _envelope()
    assert envelope["protocol"] == PROTOCOL_NAME
    assert envelope["version"] == PROTOCOL_VERSION
    assert envelope["simulation"] == {
        "id": "cannonball",
        "modelVersion": "projectile-2.0",
    }
    assert envelope["representation"] == {"kind": "linked-projectile", "version": 1}
    assert validate_frontend_envelope(envelope) == envelope


@pytest.mark.parametrize("version", [0, 2, "1"])
def test_unknown_protocol_versions_fail_closed(version: object) -> None:
    envelope = _envelope()
    envelope["version"] = version
    with pytest.raises(ValueError, match="version"):
        validate_frontend_envelope(envelope)


def test_mismatched_samples_and_nonfinite_values_are_rejected() -> None:
    envelope = _envelope()
    mismatched = deepcopy(envelope)
    mismatched["payload"]["representations"]["runs"][0]["vx_m_s"].pop()
    with pytest.raises(ValueError, match="equal lengths"):
        validate_frontend_envelope(mismatched)
    nonfinite = deepcopy(envelope)
    nonfinite["payload"]["representations"]["runs"][0]["x_m"][2] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        validate_frontend_envelope(nonfinite)


def test_protocol_module_has_no_streamlit_or_physics_implementation_dependency() -> None:
    source = __import__("pathlib").Path("physics_playground/frontend_protocol.py").read_text()
    assert "streamlit" not in source
    assert "simulate_" not in source
