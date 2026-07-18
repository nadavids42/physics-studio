from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
REMOVED_COMPATIBILITY_MODULES = (
    "accessibility.py",
    "simulation_binding.py",
    "simulation_bindings.py",
    "canvas/legacy.py",
    "missions/legacy.py",
    "presentation/accessibility.py",
    "visual/canvas.py",
)


def test_completed_compatibility_modules_are_removed() -> None:
    package = ROOT / "physics_playground"
    assert all(not (package / path).exists() for path in REMOVED_COMPATIBILITY_MODULES)


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
        source = path.read_text(encoding="utf-8")
        assert not any(item in source for item in forbidden_imports), path


def test_horizontal_page_package_has_no_python_sources() -> None:
    pages = ROOT / "physics_playground" / "pages"
    assert not pages.exists() or not tuple(pages.glob("*.py"))
