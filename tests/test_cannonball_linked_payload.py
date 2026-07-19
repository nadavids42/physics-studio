"""Envelope and invariant tests for the Cannonball linked-projectile payload."""

from copy import deepcopy
from pathlib import Path

import pytest

from physics_playground.subjects.mechanics.cannonball.linked_payload import (
    LINKED_PAYLOAD_KIND,
    LINKED_PAYLOAD_VERSION,
    linked_payload_envelope,
    validate_linked_payload_envelope,
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
    return linked_payload_envelope(
        simulation_id=result.simulation_id,
        model_version=result.model_version,
        payload=payload,
    )


def test_envelope_identifies_kind_model_and_simulation() -> None:
    envelope = _envelope()
    assert envelope["kind"] == LINKED_PAYLOAD_KIND
    assert envelope["version"] == LINKED_PAYLOAD_VERSION
    assert envelope["simulation"] == {
        "id": "cannonball",
        "modelVersion": "projectile-2.0",
    }
    assert validate_linked_payload_envelope(envelope) == envelope


@pytest.mark.parametrize("version", [0, 2, "1"])
def test_unknown_payload_versions_fail_closed(version: object) -> None:
    envelope = _envelope()
    envelope["version"] = version
    with pytest.raises(ValueError, match="version"):
        validate_linked_payload_envelope(envelope)


def test_mismatched_samples_and_nonfinite_values_are_rejected() -> None:
    envelope = _envelope()
    mismatched = deepcopy(envelope)
    mismatched["payload"]["representations"]["runs"][0]["vx_m_s"].pop()
    with pytest.raises(ValueError, match="equal lengths"):
        validate_linked_payload_envelope(mismatched)
    nonfinite = deepcopy(envelope)
    nonfinite["payload"]["representations"]["runs"][0]["x_m"][2] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        validate_linked_payload_envelope(nonfinite)


def test_module_has_no_streamlit_dependency_and_only_one_consumer() -> None:
    root = Path("physics_playground")
    module = root / "subjects/mechanics/cannonball/linked_payload.py"
    source = module.read_text()
    assert "streamlit" not in source
    assert "simulate_" not in source
    consumers = [
        path
        for path in root.rglob("*.py")
        if path != module and "linked_payload_envelope" in path.read_text()
    ]
    assert consumers == [root / "subjects/mechanics/cannonball/linked_representations.py"]
