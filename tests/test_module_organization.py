from __future__ import annotations

from pathlib import Path

from physics_playground import accessibility as old_accessibility
from physics_playground import accessibility_settings, binding_catalog, binding_models
from physics_playground import simulation_binding as old_binding_models
from physics_playground import simulation_bindings as old_binding_catalog
from physics_playground.canvas import embed
from physics_playground.canvas import legacy as old_embed
from physics_playground.missions import legacy as old_mission_ui
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation import accessibility as old_accessibility_ui
from physics_playground.presentation import accessibility_ui
from physics_playground.visual import canvas as old_primitives
from physics_playground.visual import primitives

ROOT = Path(__file__).parents[1]
COMPATIBILITY_MODULES = {
    ROOT / "physics_playground" / "accessibility.py",
    ROOT / "physics_playground" / "simulation_binding.py",
    ROOT / "physics_playground" / "simulation_bindings.py",
    ROOT / "physics_playground" / "canvas" / "legacy.py",
    ROOT / "physics_playground" / "missions" / "legacy.py",
    ROOT / "physics_playground" / "presentation" / "accessibility.py",
    ROOT / "physics_playground" / "visual" / "canvas.py",
}


def test_compatibility_modules_reexport_canonical_objects() -> None:
    assert old_accessibility.AccessibilitySettings is accessibility_settings.AccessibilitySettings
    assert old_binding_models.SimulationBinding is binding_models.SimulationBinding
    assert old_binding_catalog.SIMULATION_BINDINGS is binding_catalog.SIMULATION_BINDINGS
    assert old_embed.show is embed.show
    assert old_mission_ui.process_run is mission_ui.process_run
    assert old_accessibility_ui.render_chart is accessibility_ui.render_chart
    assert old_primitives.CANVAS_VISUAL_JS is primitives.CANVAS_VISUAL_JS


def test_internal_python_uses_only_canonical_module_paths() -> None:
    forbidden_imports = (
        "physics_playground.accessibility import",
        "physics_playground.simulation_binding import",
        "physics_playground.simulation_bindings import",
        "physics_playground.canvas import legacy",
        "physics_playground.missions import legacy",
        "physics_playground.presentation.accessibility import",
        "physics_playground.visual.canvas import",
    )
    for path in (ROOT / "physics_playground").rglob("*.py"):
        if path in COMPATIBILITY_MODULES:
            continue
        source = path.read_text(encoding="utf-8")
        assert not any(item in source for item in forbidden_imports), path


def test_horizontal_pages_do_not_alias_cached_runners_as_model_functions() -> None:
    for path in (ROOT / "physics_playground" / "pages").glob("*.py"):
        assert " as simulate_" not in path.read_text(encoding="utf-8"), path


def test_compatibility_modules_contain_no_implementations() -> None:
    for path in COMPATIBILITY_MODULES:
        source = path.read_text(encoding="utf-8")
        assert "def " not in source
        assert "class " not in source
