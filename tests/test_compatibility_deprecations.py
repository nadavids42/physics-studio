from __future__ import annotations

import pytest

from physics_playground.models import simulations
from physics_playground.state_keys import migrate_simulation_keys, simulation_key


@pytest.mark.parametrize("name", ("InteractiveMode", "SimulationMode"))
def test_legacy_mode_imports_emit_deprecation_warnings(name: str) -> None:
    with pytest.deprecated_call(match="deprecated"):
        getattr(simulations, name)


def test_persisted_simulation_alias_warns_and_migrates() -> None:
    state: dict[str, object] = {"cannon_speed": 20.0}
    with pytest.deprecated_call(match="persisted-session fixture"):
        migrate_simulation_keys(
            state,
            "cannonball",
            {"cannon_speed": "speed"},
            removal_condition="a persisted-session fixture uses only canonical keys",
        )
    assert state == {simulation_key("cannonball", "speed"): 20.0}
