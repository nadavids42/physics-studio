from dataclasses import fields

import pytest

from physics_playground.models.parameters import DoublePendulumParameters
from physics_playground.state_keys import (
    LEGACY_SHARED_KEYS,
    SHARED_STATE_KEYS,
    feature_key,
    migrate_legacy_keys,
    migrate_simulation_keys,
    simulation_key,
)
from physics_playground.subjects.fluids_and_matter.buoyancy.physics import BuoyancyParameters
from physics_playground.subjects.fluids_and_matter.fluid_pressure.physics import (
    FluidPressureParameters,
)
from physics_playground.subjects.mechanics.cannonball.physics import ProjectileParameters
from physics_playground.subjects.mechanics.inclined_plane.physics import InclinedPlaneParameters
from physics_playground.units import (
    EARTH_GRAVITY_M_S2,
    MOLAR_GAS_CONSTANT_J_MOL_K,
    ROOM_TEMPERATURE_SOUND_SPEED_M_S,
    STANDARD_ATMOSPHERE_PA,
)


def test_canonical_constants_preserve_established_defaults() -> None:
    assert EARTH_GRAVITY_M_S2 == 9.81
    assert STANDARD_ATMOSPHERE_PA == 101_325.0
    assert ROOM_TEMPERATURE_SOUND_SPEED_M_S == 343.0
    assert MOLAR_GAS_CONSTANT_J_MOL_K == 8.31446261815324
    assert ProjectileParameters(10.0, 45.0).gravity_m_s2 == 9.81
    assert DoublePendulumParameters(1, 1, 1, 1, 0, 0).gravity_m_s2 == 9.81
    assert BuoyancyParameters(1, 1, 1).gravity_m_s2 == 9.81
    assert FluidPressureParameters(1, 1).gravity_m_s2 == 9.81
    assert FluidPressureParameters(1, 1).surface_pressure_pa == 101_325.0
    assert InclinedPlaneParameters(1, 1, 0).gravity_m_s2 == 9.81


def test_shared_state_keys_are_unique_and_namespaced() -> None:
    values = [getattr(SHARED_STATE_KEYS, item.name) for item in fields(SHARED_STATE_KEYS)]
    assert len(values) == len(set(values))
    assert all(value.startswith("physics_studio.") for value in values)
    assert simulation_key("projectile", "speed") == "physics_studio.simulation.projectile.speed"


@pytest.mark.parametrize("factory", [feature_key, simulation_key])
def test_state_key_helpers_reject_empty_parts(factory) -> None:
    with pytest.raises(ValueError):
        factory("", "value")


def test_legacy_state_migration_preserves_values_and_canonical_precedence() -> None:
    old_key, canonical_key = next(iter(LEGACY_SHARED_KEYS.items()))
    state = {old_key: "legacy"}
    migrate_legacy_keys(state)
    assert state == {canonical_key: "legacy"}
    state = {old_key: "legacy", canonical_key: "current"}
    migrate_legacy_keys(state)
    assert state == {canonical_key: "current"}


def test_simulation_state_migration_uses_vertical_slice_namespace() -> None:
    state = {"old_speed": 12.0}
    migrate_simulation_keys(state, "cannonball", {"old_speed": "speed"})
    assert state == {simulation_key("cannonball", "speed"): 12.0}
