from pathlib import Path

import pytest

from physics_playground.expansion_catalog import EXPANSION_BY_ID
from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.registry import load_validated_page
from physics_playground.state_keys import simulation_key

MIGRATED = {
    "orbital_gravity": "mechanics",
    "boing": "waves_and_oscillations",
    "cannonball": "mechanics",
    "pendulum": "waves_and_oscillations",
}


@pytest.mark.parametrize(("simulation_id", "subject"), MIGRATED.items())
def test_migrated_slice_is_complete_and_manifest_validated(simulation_id, subject) -> None:
    root = Path("physics_playground/subjects") / subject / simulation_id
    assert {"physics.py", "page.py", "missions.py", "charts.py", "scene.py"} <= {
        item.name for item in root.iterdir()
    }
    validate_expansion_definition(EXPANSION_BY_ID[simulation_id])
    module, entrypoint = load_validated_page(simulation_id)
    assert module.__name__ == EXPANSION_BY_ID[simulation_id].page_entrypoint.rsplit(".", 1)[0]
    assert entrypoint == "render"


@pytest.mark.parametrize(("simulation_id", "subject"), MIGRATED.items())
def test_migrated_physics_has_no_presentation_dependencies(simulation_id, subject) -> None:
    source = (
        Path("physics_playground/subjects") / subject / simulation_id / "physics.py"
    ).read_text()
    assert "streamlit" not in source
    assert "matplotlib" not in source
    assert "physics_playground.canvas" not in source
    assert "physics_playground.presentation" not in source
    assert "physics_playground.profiles" not in source


@pytest.mark.parametrize(("simulation_id", "subject"), MIGRATED.items())
def test_migrated_page_uses_namespaced_state(simulation_id, subject) -> None:
    source = (Path("physics_playground/subjects") / subject / simulation_id / "page.py").read_text()
    assert "simulation_key" in source
    assert simulation_key(simulation_id, "learning_mode").startswith("physics_studio.simulation.")


def test_obsolete_horizontal_files_are_removed() -> None:
    old_paths = (
        "physics_playground/models/projectile.py",
        "physics_playground/pages/cannonball.py",
        "physics_playground/missions/cannonball.py",
        "physics_playground/canvas/cannonball.py",
        "physics_playground/presentation/projectile_charts.py",
        "physics_playground/models/pendulum.py",
        "physics_playground/pages/pendulum.py",
        "physics_playground/missions/pendulum.py",
        "physics_playground/canvas/pendulum.py",
        "physics_playground/presentation/pendulum_charts.py",
        "physics_playground/models/orbit.py",
        "physics_playground/pages/orbital_gravity.py",
        "physics_playground/missions/orbit.py",
        "physics_playground/canvas/orbit.py",
        "physics_playground/presentation/orbit_charts.py",
        "physics_playground/models/spring.py",
        "physics_playground/pages/boing.py",
        "physics_playground/missions/boing.py",
        "physics_playground/canvas/boing.py",
        "physics_playground/presentation/spring_charts.py",
    )
    assert not any(Path(path).exists() for path in old_paths)
