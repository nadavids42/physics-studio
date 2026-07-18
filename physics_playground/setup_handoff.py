"""Framework-neutral setup handoff shared by notebooks and lesson presets."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

from physics_playground.binding_models import SimulationPreset
from physics_playground.contracts import JsonValue

SETUP_REQUEST_KEY = "notebook_reuse_request"


@dataclass(frozen=True, slots=True)
class SimulationSetupRequest:
    simulation_id: str
    parameters: Mapping[str, JsonValue]
    source_label: str
    source_trial: int | None = None
    preset_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "parameters": dict(self.parameters),
            "source_label": self.source_label,
            "source_trial": self.source_trial,
            "preset_id": self.preset_id,
        }


def queue_setup_request(
    state: MutableMapping[str, Any],
    request: SimulationSetupRequest,
) -> None:
    state[SETUP_REQUEST_KEY] = request.to_dict()


def queue_preset(state: MutableMapping[str, Any], preset: SimulationPreset) -> None:
    queue_setup_request(
        state,
        SimulationSetupRequest(
            simulation_id=preset.simulation_id,
            parameters=preset.parameters,
            source_label=preset.title,
            preset_id=preset.id,
        ),
    )


def consume_setup_request(
    state: MutableMapping[str, Any],
    simulation_id: str,
) -> SimulationSetupRequest | None:
    payload = state.get(SETUP_REQUEST_KEY)
    if not payload or payload.get("simulation_id") != simulation_id:
        return None
    del state[SETUP_REQUEST_KEY]
    return SimulationSetupRequest(
        simulation_id=str(payload["simulation_id"]),
        parameters=dict(payload["parameters"]),
        source_label=str(payload.get("source_label") or "saved setup"),
        source_trial=payload.get("source_trial"),
        preset_id=payload.get("preset_id"),
    )
