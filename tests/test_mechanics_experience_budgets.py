"""Stable CI budgets for the completed Mechanics browser experience."""

import json

from physics_playground.subjects.mechanics.cannonball.linked_representations import (
    LINKED_JS,
    MAX_LINKED_SAMPLES,
    build_linked_projectile_document,
    linked_document_cache_info,
    linked_projectile_payload,
)
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    ProjectileResult,
    simulate_no_drag,
)


def _result(angle: float) -> ProjectileResult:
    return simulate_no_drag(ProjectileParameters(20, angle, samples=240))


def test_linked_bundle_and_payload_size_budgets() -> None:
    runs = (("30 degrees", _result(30)), ("60 degrees", _result(60)))
    payload = linked_projectile_payload(runs, target_m=40)
    payload_size = len(json.dumps(payload, separators=(",", ":")).encode())
    assert len(LINKED_JS.encode()) <= 85_000
    assert payload_size <= 50_000
    assert all(
        len(run["time_s"]) <= MAX_LINKED_SAMPLES for run in payload["representations"]["runs"]
    )


def test_unrelated_rebuild_uses_identical_document_without_player_remount() -> None:
    runs = (("Current run", _result(45)),)
    before = linked_document_cache_info()
    first = build_linked_projectile_document(runs, target_m=40)
    second = build_linked_projectile_document(runs, target_m=40)
    after = linked_document_cache_info()
    assert first == second
    assert after.hits > before.hits
    assert first.count("window.linkedProjectile=mountLinkedProjectile(") == 1


def test_cache_and_sample_caps_bound_long_session_memory_growth() -> None:
    info = linked_document_cache_info()
    assert info.maxsize <= 32
    assert MAX_LINKED_SAMPLES <= 120
