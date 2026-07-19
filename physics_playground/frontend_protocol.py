"""Versioned Python-to-frontend protocol for incrementally migrated experiences."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TypeAlias, cast

from physics_playground.contracts import JsonValue

PROTOCOL_NAME = "physics-studio.frontend"
PROTOCOL_VERSION = 1

FrontendEnvelope: TypeAlias = dict[str, JsonValue]


def linked_projectile_envelope(
    *, simulation_id: str, model_version: str, payload: Mapping[str, JsonValue]
) -> FrontendEnvelope:
    """Wrap a validated linked-projectile payload in protocol version 1."""

    envelope: FrontendEnvelope = {
        "protocol": PROTOCOL_NAME,
        "version": PROTOCOL_VERSION,
        "simulation": {"id": simulation_id, "modelVersion": model_version},
        "representation": {"kind": "linked-projectile", "version": 1},
        "payload": dict(payload),
    }
    validate_frontend_envelope(envelope)
    return envelope


def _require_object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Frontend protocol {label} must be an object.")
    return value


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Frontend protocol {label} must be nonblank text.")
    return value


def _numeric_array(value: object, label: str) -> Sequence[int | float]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Frontend protocol {label} must be a nonempty array.")
    if any(
        isinstance(item, bool)
        or not isinstance(item, int | float)
        or not math.isfinite(float(item))
        for item in value
    ):
        raise ValueError(f"Frontend protocol {label} must contain finite numbers.")
    return value


def validate_frontend_envelope(value: object) -> FrontendEnvelope:
    """Validate the supported v1 envelope and linked-projectile invariant."""

    envelope = _require_object(value, "envelope")
    if envelope.get("protocol") != PROTOCOL_NAME:
        raise ValueError("Unsupported frontend protocol name.")
    if envelope.get("version") != PROTOCOL_VERSION:
        raise ValueError("Unsupported frontend protocol version.")
    simulation = _require_object(envelope.get("simulation"), "simulation")
    _require_text(simulation.get("id"), "simulation ID")
    _require_text(simulation.get("modelVersion"), "model version")
    representation = _require_object(envelope.get("representation"), "representation")
    if representation.get("kind") != "linked-projectile" or representation.get("version") != 1:
        raise ValueError("Unsupported frontend representation contract.")
    payload = _require_object(envelope.get("payload"), "payload")
    duration = payload.get("durationMs")
    if isinstance(duration, bool) or not isinstance(duration, int | float) or duration <= 0:
        raise ValueError("Linked-projectile payload requires a positive durationMs.")
    representations = _require_object(payload.get("representations"), "representations")
    runs = representations.get("runs")
    tracks = payload.get("tracks")
    if not isinstance(runs, list) or not runs or not isinstance(tracks, list):
        raise ValueError("Linked-projectile payload requires runs and tracks.")
    if len(runs) != len(tracks):
        raise ValueError("Linked-projectile runs and tracks must correspond one-to-one.")
    keys = ("time_s", "x_m", "y_m", "vx_m_s", "vy_m_s", "ax_m_s2", "ay_m_s2")
    for index, run_value in enumerate(runs):
        run = _require_object(run_value, f"run {index}")
        _require_text(run.get("label"), f"run {index} label")
        arrays = [_numeric_array(run.get(key), f"run {index} {key}") for key in keys]
        if len({len(item) for item in arrays}) != 1:
            raise ValueError("Linked-projectile run arrays must have equal lengths.")
        times = arrays[0]
        if any(float(right) <= float(left) for left, right in zip(times, times[1:], strict=False)):
            raise ValueError("Linked-projectile time samples must be strictly increasing.")
    return cast(FrontendEnvelope, dict(envelope))
