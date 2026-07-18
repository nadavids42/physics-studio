import dataclasses
import json
from importlib import import_module, util
from pathlib import Path

from physics_playground.expansion_catalog import (
    EXPANSION_MANIFESTS,
    parameter_type,
    resolve_entrypoint,
)
from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.models.simulations import SimulationMode
from physics_playground.notebook import ExperimentNotebook
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.serialization import dataclass_from_dict, to_jsonable

EXPANSION_IDS = {
    "inclined_plane",
    "torque_levers",
    "center_of_mass",
    "roller_coaster",
    "rotational_motion",
    "wave_interference",
    "doppler_effect",
    "reflection_refraction",
    "thin_lenses",
    "electric_fields",
    "magnetic_forces",
    "buoyancy",
    "fluid_pressure",
    "gas_laws",
    "diffusion",
}
LEARNING_MODES = {
    SimulationMode.EXPLORE,
    SimulationMode.COMPARE,
    SimulationMode.ANALYZE,
    SimulationMode.MODEL,
}


def test_every_expansion_is_registered_reachable_and_contract_complete() -> None:
    assert {item.metadata.id for item in EXPANSION_MANIFESTS} == EXPANSION_IDS
    for manifest in EXPANSION_MANIFESTS:
        validate_expansion_definition(manifest)
        definition = SIMULATIONS_BY_ID[manifest.metadata.id]
        assert set(definition.modes) == LEARNING_MODES
        assert util.find_spec(manifest.page_entrypoint.rsplit(".", 1)[0])
        assert resolve_entrypoint(manifest.physics_entrypoint)
        assert manifest.canvas_entrypoint and len(manifest.missions) >= 3
        assert manifest.assumptions and manifest.limitations


def test_parameter_and_result_models_are_typed_dataclasses() -> None:
    for manifest in EXPANSION_MANIFESTS:
        model = parameter_type(manifest)
        assert dataclasses.is_dataclass(model)
        result = resolve_entrypoint(manifest.physics_entrypoint)(model())
        assert dataclasses.is_dataclass(result)


def test_all_parameter_models_round_trip_through_notebook_json() -> None:
    notebook = ExperimentNotebook()
    for manifest in EXPANSION_MANIFESTS:
        original = parameter_type(manifest)()
        payload = to_jsonable(original)
        restored = dataclass_from_dict(type(original), payload)
        assert restored == original
        notebook.add_trial(
            simulation_id=manifest.metadata.id,
            parameters=payload,
            prediction=None,
            result_summary="audit",
            metrics={"value": 1.0},
            earned_badges=(),
            random_seed=1,
            model_version=manifest.metadata.model_version,
        )
    decoded = json.loads(notebook.to_json())
    restored_notebook = ExperimentNotebook.from_dict(decoded)
    assert len(restored_notebook.trials) == len(EXPANSION_MANIFESTS)
    assert json.loads(restored_notebook.to_json()) == decoded


def test_pages_expose_all_modes_notebook_assumptions_and_safe_keys() -> None:
    mode_names = {mode.name for mode in LEARNING_MODES}
    seen_mode_keys = set()
    for manifest in EXPANSION_MANIFESTS:
        spec = util.find_spec(manifest.page_entrypoint.rsplit(".", 1)[0])
        assert spec and spec.origin
        source = Path(spec.origin).read_text()
        assert all(f"LearningMode.{name}" in source for name in mode_names)
        assert "assumptions_panel" in source
        assert "process_run" in source
        assert "record(" in source or "add_trial(" in source
        marker = 'mode_navigation(key="'
        start = source.index(marker) + len(marker)
        key = source[start : source.index('"', start)]
        assert key not in seen_mode_keys
        seen_mode_keys.add(key)


def test_canvas_entrypoints_use_shared_player_documents() -> None:
    for manifest in EXPANSION_MANIFESTS:
        module_name = manifest.canvas_entrypoint.rsplit(".", 1)[0]
        source = Path(import_module(module_name).__file__).read_text()
        assert "build_player_document" in source


def test_specialized_fluid_manifests_match_runtime_renderers() -> None:
    by_id = {item.metadata.id: item for item in EXPANSION_MANIFESTS}
    assert by_id["diffusion"].canvas_entrypoint.endswith(
        "diffusion_player.build_diffusion_document"
    )
    assert by_id["gas_laws"].canvas_entrypoint.endswith("gas_container.build_gas_document")
